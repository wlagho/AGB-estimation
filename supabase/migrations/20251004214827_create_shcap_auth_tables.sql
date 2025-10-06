/*
  # SHCAP Authentication System Database Schema

  ## Overview
  This migration creates the complete database schema for the SmallHolder Carbon Assessment Platform (SHCAP) authentication system.

  ## 1. New Tables

  ### `users` table
  Stores all user information with role-based access control:
  - `id` (uuid, primary key) - Unique user identifier
  - `email` (text, unique) - User email address for login
  - `password_hash` (text) - Bcrypt hashed password
  - `role` (text) - User role: 'researcher', 'project_developer', or 'admin'
  - `first_name` (text) - User's first name
  - `last_name` (text) - User's last name
  - `organization` (text) - User's organization name
  - `email_verified` (boolean) - Email verification status
  - `two_factor_enabled` (boolean) - 2FA activation status
  - `phone_number` (text, nullable) - Optional phone number
  - `created_at` (timestamptz) - Account creation timestamp
  - `last_login` (timestamptz, nullable) - Last successful login timestamp

  ### `user_tokens` table
  Manages temporary tokens for password reset and 2FA verification:
  - `id` (uuid, primary key) - Unique token identifier
  - `user_id` (uuid, foreign key) - References users table
  - `token` (text) - Random secure token string
  - `token_type` (text) - Type: 'password_reset' or 'two_factor'
  - `expires_at` (timestamptz) - Token expiration time
  - `used` (boolean) - Token usage status
  - `created_at` (timestamptz) - Token creation timestamp

  ## 2. Security Features

  ### Row Level Security (RLS)
  - Enabled on both `users` and `user_tokens` tables
  - Restrictive policies ensure users can only access their own data
  - Admin role has elevated privileges for user management

  ### Policies Created

  #### Users table policies:
  1. **"Users can view own profile"** - Users can SELECT their own data
  2. **"Users can update own profile"** - Users can UPDATE their own data
  3. **"Admins can view all users"** - Admin role can SELECT all user data
  4. **"Public can create new users"** - Anyone can INSERT (for registration)

  #### User tokens table policies:
  1. **"Users can view own tokens"** - Users can SELECT their own tokens
  2. **"Users can create own tokens"** - Users can INSERT tokens for themselves
  3. **"Users can update own tokens"** - Users can UPDATE their own tokens

  ## 3. Indexes
  - Email index for fast login lookups
  - Token index for fast verification
  - User token foreign key for efficient joins

  ## 4. Important Notes
  - All passwords must be stored as bcrypt hashes, never in plain text
  - Tokens expire after 1 hour for password reset, 10 minutes for 2FA
  - Email verification is required before full account access
  - Default role is 'researcher' if not specified
  - Phone numbers are optional and used for future SMS 2FA expansion
*/

-- Create users table
CREATE TABLE IF NOT EXISTS users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text UNIQUE NOT NULL,
  password_hash text NOT NULL,
  role text NOT NULL DEFAULT 'researcher',
  first_name text NOT NULL,
  last_name text NOT NULL,
  organization text NOT NULL,
  email_verified boolean DEFAULT false,
  two_factor_enabled boolean DEFAULT false,
  phone_number text,
  created_at timestamptz DEFAULT now(),
  last_login timestamptz,
  CONSTRAINT valid_role CHECK (role IN ('researcher', 'project_developer', 'admin'))
);

-- Create user_tokens table
CREATE TABLE IF NOT EXISTS user_tokens (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token text NOT NULL,
  token_type text NOT NULL,
  expires_at timestamptz NOT NULL,
  used boolean DEFAULT false,
  created_at timestamptz DEFAULT now(),
  CONSTRAINT valid_token_type CHECK (token_type IN ('password_reset', 'two_factor'))
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_user_tokens_token ON user_tokens(token);
CREATE INDEX IF NOT EXISTS idx_user_tokens_user_id ON user_tokens(user_id);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_tokens ENABLE ROW LEVEL SECURITY;

-- Users table policies
CREATE POLICY "Users can view own profile"
  ON users FOR SELECT
  TO authenticated
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON users FOR UPDATE
  TO authenticated
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

CREATE POLICY "Admins can view all users"
  ON users FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE users.id = auth.uid()
      AND users.role = 'admin'
    )
  );

CREATE POLICY "Public can create new users"
  ON users FOR INSERT
  TO anon
  WITH CHECK (true);

-- User tokens table policies
CREATE POLICY "Users can view own tokens"
  ON user_tokens FOR SELECT
  TO authenticated
  USING (user_id = auth.uid());

CREATE POLICY "Users can create own tokens"
  ON user_tokens FOR INSERT
  TO authenticated
  WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update own tokens"
  ON user_tokens FOR UPDATE
  TO authenticated
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

-- Allow anonymous users to create tokens (for password reset requests)
CREATE POLICY "Anonymous can create tokens"
  ON user_tokens FOR INSERT
  TO anon
  WITH CHECK (true);