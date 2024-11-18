from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "conversions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "user_currency" VARCHAR(10) NOT NULL,
    "exchange_currency" VARCHAR(10) NOT NULL,
    "course" DECIMAL(10,2) NOT NULL,
    "clean_course" DECIMAL(10,2) NOT NULL,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE "conversions" IS 'Конвертация';
CREATE TABLE IF NOT EXISTS "graduations" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "min_amount" DECIMAL(10,2) NOT NULL,
    "max_amount" DECIMAL(10,2) NOT NULL,
    "adjustment" DECIMAL(10,2) NOT NULL
);
COMMENT ON TABLE "graduations" IS 'Градация';
CREATE TABLE IF NOT EXISTS "order_statuses" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT
);
COMMENT ON TABLE "order_statuses" IS 'Статусы заказов';
CREATE TABLE IF NOT EXISTS "order_types" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT
);
COMMENT ON TABLE "order_types" IS 'Типы заказов';
CREATE TABLE IF NOT EXISTS "roles" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "can_create" BOOL NOT NULL  DEFAULT False,
    "can_edit" BOOL NOT NULL  DEFAULT False,
    "can_delete" BOOL NOT NULL  DEFAULT False,
    "can_view" BOOL NOT NULL  DEFAULT False
);
COMMENT ON TABLE "roles" IS 'Роли';
CREATE TABLE IF NOT EXISTS "users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "username" VARCHAR(255) NOT NULL UNIQUE,
    "user_id" BIGINT NOT NULL UNIQUE,
    "first_name" VARCHAR(255),
    "description" VARCHAR(255),
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "promocodes" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "code" VARCHAR(50) NOT NULL UNIQUE,
    "discount" DECIMAL(10,2) NOT NULL,
    "percent" BOOL NOT NULL  DEFAULT False,
    "activations" INT NOT NULL  DEFAULT 0,
    "max_activations" INT,
    "one_time" BOOL NOT NULL  DEFAULT False,
    "start_at" TIMESTAMPTZ,
    "end_at" TIMESTAMPTZ,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "order_type_id" INT REFERENCES "order_types" ("id") ON DELETE CASCADE,
    "user_id" INT REFERENCES "users" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "promocodes" IS 'Промокоды';
CREATE TABLE IF NOT EXISTS "orders" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "order_id" INT NOT NULL UNIQUE,
    "contact_method" VARCHAR(255) NOT NULL,
    "amount" DECIMAL(10,2) NOT NULL,
    "exchange_rate" DECIMAL(10,6),
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "conversion_id" INT REFERENCES "conversions" ("id") ON DELETE CASCADE,
    "promocode_id" INT REFERENCES "promocodes" ("id") ON DELETE CASCADE,
    "status_id" INT NOT NULL REFERENCES "order_statuses" ("id") ON DELETE CASCADE,
    "type_id" INT NOT NULL REFERENCES "order_types" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "orders" IS 'Заказы';
CREATE TABLE IF NOT EXISTS "promocode_usages" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "promocode_id" INT NOT NULL REFERENCES "promocodes" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "promocode_usages" IS 'Использование промокодов';
CREATE TABLE IF NOT EXISTS "user_activities" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "activity_type" VARCHAR(255) NOT NULL,
    "device" VARCHAR(255),
    "ip_address" VARCHAR(45),
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "user_roles" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "role_id" INT NOT NULL REFERENCES "roles" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_user_roles_user_id_63f1a8" UNIQUE ("user_id", "role_id")
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "conversions_graduations" (
    "conversions_id" INT NOT NULL REFERENCES "conversions" ("id") ON DELETE CASCADE,
    "graduations_id" INT NOT NULL REFERENCES "graduations" ("id") ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS "uidx_conversions_convers_70f50d" ON "conversions_graduations" ("conversions_id", "graduations_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
