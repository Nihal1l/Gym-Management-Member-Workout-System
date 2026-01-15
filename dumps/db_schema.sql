-- Gym Management API - Database Schema Dump
-- Generated: January 15, 2026
-- Database: SQLite 3.x / PostgreSQL 12+
-- Format: SQL (DDL only - schema definition)

-- ============================================
-- USER TABLE
-- ============================================

CREATE TABLE gym_api_user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME,
    is_superuser BOOLEAN NOT NULL DEFAULT 0,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    email VARCHAR(254) NOT NULL UNIQUE,
    is_staff BOOLEAN NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    date_joined DATETIME NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'member',
    gym_branch_id INTEGER,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (gym_branch_id) REFERENCES gym_api_gymbranch(id)
);

CREATE INDEX gym_api_user_email ON gym_api_user(email);
CREATE INDEX gym_api_user_role ON gym_api_user(role);
CREATE INDEX gym_api_user_gym_branch_id ON gym_api_user(gym_branch_id);

-- Role Choices:
-- 'super_admin' - Super Admin
-- 'gym_manager' - Gym Manager
-- 'trainer' - Trainer
-- 'member' - Member

-- ============================================
-- GYM BRANCH TABLE
-- ============================================

CREATE TABLE gym_api_gymbranch (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE INDEX gym_api_gymbranch_name ON gym_api_gymbranch(name);
CREATE INDEX gym_api_gymbranch_is_active ON gym_api_gymbranch(is_active);

-- ============================================
-- WORKOUT PLAN TABLE
-- ============================================

CREATE TABLE gym_api_workoutplan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    created_by_id INTEGER NOT NULL,
    gym_branch_id INTEGER NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (created_by_id) REFERENCES gym_api_user(id),
    FOREIGN KEY (gym_branch_id) REFERENCES gym_api_gymbranch(id)
);

CREATE INDEX gym_api_workoutplan_gym_branch_created_by 
    ON gym_api_workoutplan(gym_branch_id, created_by_id);
CREATE INDEX gym_api_workoutplan_created_at 
    ON gym_api_workoutplan(created_at);

-- Constraint: created_by must have role='trainer'
-- Constraint: created_by.gym_branch == gym_branch

-- ============================================
-- WORKOUT TASK TABLE
-- ============================================

CREATE TABLE gym_api_workoutask (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    due_date DATETIME NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    created_by_id INTEGER NOT NULL,
    member_id INTEGER NOT NULL,
    workout_plan_id INTEGER NOT NULL,
    FOREIGN KEY (created_by_id) REFERENCES gym_api_user(id),
    FOREIGN KEY (member_id) REFERENCES gym_api_user(id),
    FOREIGN KEY (workout_plan_id) REFERENCES gym_api_workoutplan(id)
);

CREATE INDEX gym_api_workoutask_member_status 
    ON gym_api_workoutask(member_id, status);
CREATE INDEX gym_api_workoutask_workout_plan_member 
    ON gym_api_workoutask(workout_plan_id, member_id);
CREATE INDEX gym_api_workoutask_created_at 
    ON gym_api_workoutask(created_at);
CREATE INDEX gym_api_workoutask_due_date 
    ON gym_api_workoutask(due_date);

-- Status Choices:
-- 'pending' - Pending
-- 'in_progress' - In Progress
-- 'completed' - Completed

-- Constraint: member must have role='member'
-- Constraint: created_by must have role='trainer'
-- Constraint: member.gym_branch == workout_plan.gym_branch
-- Constraint: created_by.gym_branch == workout_plan.gym_branch

-- ============================================
-- ACTIVITY LOG TABLE
-- ============================================

CREATE TABLE gym_api_activitylog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action VARCHAR(20) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    object_id VARCHAR(100) NOT NULL,
    changes TEXT NOT NULL DEFAULT '{}',
    created_at DATETIME NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES gym_api_user(id)
);

CREATE INDEX gym_api_activitylog_user_created_at 
    ON gym_api_activitylog(user_id, created_at);
CREATE INDEX gym_api_activitylog_created_at 
    ON gym_api_activitylog(created_at);

-- Action Choices:
-- 'create' - Create
-- 'update' - Update
-- 'delete' - Delete
-- 'login' - Login

-- ============================================
-- FOREIGN KEY CASCADE RULES
-- ============================================

-- CASCADE DELETE Rules:
-- GymBranch -> User: ON DELETE CASCADE
-- GymBranch -> WorkoutPlan: ON DELETE CASCADE
-- WorkoutPlan -> WorkoutTask: ON DELETE CASCADE
-- User (created_by) -> WorkoutPlan: ON DELETE CASCADE
-- User (created_by) -> WorkoutTask: ON DELETE SET_NULL
-- User -> ActivityLog: ON DELETE CASCADE

-- ============================================
-- SAMPLE DATA AFTER create_test_data
-- ============================================

-- 2 Gym Branches:
-- 1. Downtown Gym (123 Main St, City Center)
-- 2. Uptown Gym (456 Oak Ave, Uptown)

-- 9 Users:
-- 1. superadmin@gym.com / SuperAdmin@123 (super_admin, no branch)
-- 2. manager1@gym.com / Manager@123 (gym_manager, Downtown)
-- 3. manager2@gym.com / Manager@123 (gym_manager, Uptown)
-- 4. trainer1@gym.com / Trainer@123 (trainer, Downtown)
-- 5. trainer2@gym.com / Trainer@123 (trainer, Downtown)
-- 6. trainer3@gym.com / Trainer@123 (trainer, Uptown)
-- 7. member1@gym.com / Member@123 (member, Downtown)
-- 8. member2@gym.com / Member@123 (member, Downtown)
-- 9. member3@gym.com / Member@123 (member, Uptown)

-- 2 Workout Plans:
-- 1. Full Body Workout (Downtown)
-- 2. Upper Body Workout (Downtown)

-- 6 Workout Tasks:
-- Assigned to members from trainers

-- ============================================
-- ADDITIONAL INDEXES FOR PERFORMANCE
-- ============================================

-- Already created above, but summary:
-- 1. User: email, role, gym_branch_id
-- 2. GymBranch: name, is_active
-- 3. WorkoutPlan: (gym_branch, created_by), created_at
-- 4. WorkoutTask: (member, status), (workout_plan, member), created_at, due_date
-- 5. ActivityLog: (user, created_at), created_at

-- ============================================
-- MIGRATION HISTORY
-- ============================================

-- Migration: 0001_initial
-- - Created all 5 main tables
-- - Added all indexes
-- - Added all foreign key constraints

-- ============================================
-- DATABASE STATISTICS
-- ============================================

-- Table: gym_api_user
--   Columns: 15
--   Test Rows: 9
--   Indexes: 3

-- Table: gym_api_gymbranch
--   Columns: 5
--   Test Rows: 2
--   Indexes: 2

-- Table: gym_api_workoutplan
--   Columns: 7
--   Test Rows: 2
--   Indexes: 2

-- Table: gym_api_workoutask
--   Columns: 8
--   Test Rows: 6
--   Indexes: 4

-- Table: gym_api_activitylog
--   Columns: 7
--   Test Rows: varies
--   Indexes: 2

-- Total Indexes: 13

-- ============================================
-- NOTES FOR POSTGRESQL
-- ============================================

-- For PostgreSQL deployment:
-- 1. Replace INTEGER with BIGSERIAL for id columns
-- 2. Replace DATETIME with TIMESTAMP for datetime fields
-- 3. Replace TEXT for JSON fields with JSONB for better performance
-- 4. Add CONSTRAINTS to ensure referential integrity
-- 5. Consider partitioning ActivityLog by date for very large tables

-- ============================================
-- END OF SCHEMA DUMP
-- ============================================
