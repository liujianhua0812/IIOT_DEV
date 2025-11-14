-- 数据库初始化 SQL 脚本
-- 数据库：iiot_platform
-- 服务器：166.111.80.127:15432

-- 创建组织表
CREATE TABLE IF NOT EXISTS organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    english_name VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE organizations IS '组织表';
COMMENT ON COLUMN organizations.id IS '组织ID';
COMMENT ON COLUMN organizations.name IS '组织名称';
COMMENT ON COLUMN organizations.english_name IS '组织英文名';
COMMENT ON COLUMN organizations.description IS '组织描述';
COMMENT ON COLUMN organizations.created_at IS '创建时间';
COMMENT ON COLUMN organizations.updated_at IS '更新时间';

-- 创建应用表
CREATE TABLE IF NOT EXISTS applications (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    english_name VARCHAR(100),
    organization_id INTEGER NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_organization 
        FOREIGN KEY (organization_id) 
        REFERENCES organizations(id) 
        ON DELETE CASCADE
);

COMMENT ON TABLE applications IS '应用表';
COMMENT ON COLUMN applications.id IS '应用ID';
COMMENT ON COLUMN applications.name IS '应用名称';
COMMENT ON COLUMN applications.english_name IS '应用英文名';
COMMENT ON COLUMN applications.organization_id IS '所属组织ID';
COMMENT ON COLUMN applications.description IS '应用描述';
COMMENT ON COLUMN applications.created_at IS '创建时间';
COMMENT ON COLUMN applications.updated_at IS '更新时间';

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_applications_organization_id ON applications(organization_id);
CREATE INDEX IF NOT EXISTS idx_applications_name ON applications(name);

