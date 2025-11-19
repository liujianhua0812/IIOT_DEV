import time
import uuid
import threading
from dataclasses import dataclass
from collections import deque
from datetime import datetime, timezone

import simpy
from simpy.rt import RealtimeEnvironment

from database import (
    SessionLocal,
    ProductionOrder,
    ProductionProduct,
)


@dataclass
class StationTimes:
    belt_to_scanner: float = 2.0
    scan_time: float = 1.0
    belt_to_stop: float = 1.5
    jack_up: float = 0.5
    mbi_query: float = 0.5
    feeder_time: float = 0.8
    robot_pick: float = 1.0
    robot_to_loc_cam: float = 0.6
    locating_time: float = 0.4
    robot_to_device: float = 0.7
    labeling_time: float = 1.2
    jack_down: float = 0.5
    belt_to_inspection: float = 1.8
    qc_time: float = 0.8


class ProductionSimulator:
    """Simulates orders by updating database records and emitting log events using SimPy RealtimeEnvironment."""

    def __init__(
        self,
        session_factory=SessionLocal,
        station_times: StationTimes = StationTimes(),
        poll_interval: float = 5.0,
        labels_per_product: int = 1,
        max_events: int = 400,
        realtime_factor: float = 1.0,
    ):
        self.session_factory = session_factory
        self.station_times = station_times
        self.poll_interval = poll_interval
        self.labels_per_product = max(1, labels_per_product)
        self.realtime_factor = realtime_factor
        self.events = deque(maxlen=max_events)
        self.running = False
        self.thread = None
        self.websocket_callback = None  # Callback function to push events via WebSocket

    # ----------------- lifecycle -----------------
    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)

    # ----------------- main loop -----------------
    def _run_loop(self):
        while self.running:
            session = self.session_factory()
            try:
                order = (
                    session.query(ProductionOrder)
                    .filter(ProductionOrder.status == "scheduled")
                    .order_by(
                        ProductionOrder.scheduled_date.is_(None),
                        ProductionOrder.scheduled_date.asc(),
                        ProductionOrder.id.asc(),
                    )
                    .first()
                )

                if not order:
                    time.sleep(self.poll_interval)
                    continue

                self._log_event(
                    "order_pick",
                    f"选中订单 {order.order_code or order.id}",
                    order_id=order.id,
                    order_code=order.order_code,
                )

                order.status = "in_progress"
                session.commit()
                self._log_event(
                    "order_in_progress",
                    "订单开始执行",
                    order_id=order.id,
                    order_code=order.order_code,
                )

                products = (
                    session.query(ProductionProduct)
                    .filter(
                        ProductionProduct.order_id == order.id,
                    )
                    .order_by(ProductionProduct.id.asc())
                    .all()
                )

                for product in products:
                    if product.status != "scheduled":
                        continue
                    # Create a new RealtimeEnvironment for each product
                    env = RealtimeEnvironment(factor=self.realtime_factor, strict=True)
                    # Start the simulation process
                    process = env.process(self._simulate_product(env, session, order, product))
                    # Calculate a reasonable timeout (sum of all steps + buffer)
                    total_time = (
                        self.station_times.belt_to_scanner
                        + self.station_times.scan_time
                        + self.station_times.belt_to_stop
                        + self.station_times.jack_up
                        + self.station_times.mbi_query
                        + self.labels_per_product * (
                            self.station_times.feeder_time
                            + self.station_times.robot_pick
                            + self.station_times.robot_to_loc_cam
                            + self.station_times.locating_time
                            + self.station_times.robot_to_device
                            + self.station_times.labeling_time
                        )
                        + self.station_times.jack_down
                        + self.station_times.belt_to_inspection
                        + self.station_times.qc_time
                        + 5.0  # buffer
                    )
                    # Run the environment until the process completes
                    env.run(until=total_time)

                order.status = "completed"
                order.updated_at = datetime.now(timezone.utc)
                session.commit()
                self._log_event(
                    "order_completed",
                    "订单全部产品完成",
                    order_id=order.id,
                    order_code=order.order_code,
                )
            except Exception as exc:
                session.rollback()
                self._log_event("error", f"模拟异常: {exc}")
                time.sleep(self.poll_interval)
            finally:
                session.close()

    # ----------------- simulation helpers -----------------
    def _simulate_product(self, env: RealtimeEnvironment, session, order, product):
        """SimPy process to simulate a single product through the production line."""
        # Update product status to in_progress
        product.status = "in_progress"
        product.updated_at = datetime.now(timezone.utc)
        session.commit()
        self._log_event(
            "product_start",
            f"产品 {product.serial_number} 开始上线",
            order_id=order.id,
            order_code=order.order_code,
            product_id=product.id,
            product_sn=product.serial_number,
        )

        # Belt to scanner
        yield from self._step(env, self.station_times.belt_to_scanner, "belt", "设备移动到扫码位", order, product)
        
        # Scan
        yield from self._step(env, self.station_times.scan_time, "scanner", "扫码相机读码", order, product)
        
        # Belt to stop position
        yield from self._step(env, self.station_times.belt_to_stop, "belt", "移动到挡停位置", order, product)
        
        # Jack up and light on
        yield from self._step(env, self.station_times.jack_up, "lifters", "顶升气缸抬起，光源点亮", order, product)
        
        # Query MBI server
        yield from self._step(env, self.station_times.mbi_query, "mbi", "MBI Server 返回产品参数", order, product)

        # Label cycles
        for cycle in range(self.labels_per_product):
            cycle_label = f"{cycle + 1}/{self.labels_per_product}"
            yield from self._step(env, self.station_times.feeder_time, "feeder", f"进料器供料 {cycle_label}", order, product)
            yield from self._step(env, self.station_times.robot_pick, "robot", f"机械臂取标 {cycle_label}", order, product)
            yield from self._step(env, self.station_times.robot_to_loc_cam, "robot", "机械臂移动至定位相机", order, product)
            yield from self._step(env, self.station_times.locating_time, "camera", "定位相机校准", order, product)
            yield from self._step(env, self.station_times.robot_to_device, "robot", "机械臂移动至设备", order, product)
            yield from self._step(env, self.station_times.labeling_time, "labeling", "执行贴码", order, product)

        # Jack down and light off
        yield from self._step(env, self.station_times.jack_down, "lifters", "顶升气缸复位，光源熄灭", order, product)
        
        # Belt to inspection
        yield from self._step(env, self.station_times.belt_to_inspection, "belt", "设备前往质检位", order, product)
        
        # QC camera
        yield from self._step(env, self.station_times.qc_time, "qc", "质检相机拍照", order, product)

        # Update product status to completed
        product.status = "completed"
        product.produced_end = datetime.now(timezone.utc)
        product.updated_at = datetime.now(timezone.utc)
        session.commit()

        self._log_event(
            "product_completed",
            f"产品 {product.serial_number} 完成",
            order_id=order.id,
            order_code=order.order_code,
            product_id=product.id,
            product_sn=product.serial_number,
        )

    def _step(self, env: RealtimeEnvironment, duration: float, stage: str, message: str, order, product):
        """SimPy process step that logs and waits for the specified duration."""
        self._log_event(
            stage,
            message,
            order_id=order.id if order else None,
            order_code=order.order_code if order else None,
            product_id=product.id if product else None,
            product_sn=product.serial_number if product else None,
        )
        yield env.timeout(duration)

    # ----------------- event utils -----------------
    def set_websocket_callback(self, callback):
        """Set a callback function to push events via WebSocket."""
        self.websocket_callback = callback

    def _format_log_message(self, stage, message, **context):
        """Format log message to match the log file format."""
        # Map stage to log level and source
        stage_map = {
            "order_pick": ("INFO", "OrderManager"),
            "order_in_progress": ("INFO", "OrderManager"),
            "order_completed": ("INFO", "OrderManager"),
            "product_start": ("INFO", "ProductionLine"),
            "product_completed": ("INFO", "ProductionLine"),
            "belt": ("INFO", "ConveyorBelt"),
            "scanner": ("INFO", "ScannerCamera"),
            "lifters": ("INFO", "Lifters"),
            "mbi": ("INFO", "MBIServer"),
            "feeder": ("INFO", "Feeder"),
            "robot": ("INFO", "RobotArm"),
            "camera": ("INFO", "Camera"),
            "labeling": ("INFO", "Labeling"),
            "qc": ("INFO", "QCCamera"),
            "error": ("ERROR", "System"),
        }
        
        level, source = stage_map.get(stage, ("INFO", "System"))
        
        # Format message with context
        log_parts = [message]
        if context.get("order_code"):
            log_parts.append(f"订单:{context['order_code']}")
        if context.get("product_sn"):
            log_parts.append(f"产品:{context['product_sn']}")
        
        formatted_message = " | ".join(log_parts)
        
        return level, source, formatted_message

    def _log_event(self, stage, message, **context):
        # Get current time in the log file format: YYYY-MM-DD HH:MM:SS,mmm
        now = datetime.now(timezone.utc)
        timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S") + f",{now.microsecond // 1000:03d}"
        
        # Format log message
        level, source, formatted_message = self._format_log_message(stage, message, **context)
        
        # Create formatted log line matching the log file format
        # Format: YYYY-MM-DD HH:MM:SS,mmm[6 ] | [LEVEL] [SOURCE] | MESSAGE
        thread_id = "6 "  # Fixed thread ID as in log file
        log_line = f"{timestamp_str}[{thread_id}] | [{level:5}] [{source}] | {formatted_message}"
        
        # Print to console (matching log file format)
        print(log_line)
        
        # Create event object for WebSocket
        event = {
            "id": str(uuid.uuid4()),
            "timestamp": now.isoformat(),
            "stage": stage,
            "message": formatted_message,
            "log_line": log_line,  # Add formatted log line
            "level": level,
            "source": source,
        }
        event.update(context)
        self.events.appendleft(event)
        
        # Push event via WebSocket immediately if callback is set
        if self.websocket_callback:
            try:
                # Immediately push each event to WebSocket
                self.websocket_callback(event)
            except Exception as e:
                # Don't break simulation if WebSocket push fails
                print(f"WebSocket push failed: {e}")

    def get_events(self, limit: int = 100):
        if not self.events:
            return []
        limit = max(1, min(limit, len(self.events)))
        return list(self.events)[:limit]


def create_simulator():
    simulator = ProductionSimulator()
    simulator.start()
    return simulator

