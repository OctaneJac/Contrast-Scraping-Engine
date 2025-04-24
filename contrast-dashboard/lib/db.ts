// lib/db.ts
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.POSTGRES_URI, // set this in your .env file
});

export default pool;
