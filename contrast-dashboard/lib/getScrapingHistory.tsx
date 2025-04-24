// lib/getScrapingHistory.ts
import pool from "./db";

export async function getScrapingHistory() {
  const client = await pool.connect();

  try {
    const result = await client.query(`
      SELECT 
        scraper_name,
        celery_trigger_time,
        actual_start_time,
        end_time,
        duration_seconds,
        retries,
        result,
        error
      FROM spider_logs
      ORDER BY celery_trigger_time DESC
      LIMIT 100
    `);

    return result.rows.map((row: any) => ({
      scraper_name: row.scraper_name,
      celery_trigger_time: row.celery_trigger_time,
      actual_start_time: row.actual_start_time,
      end_time: row.end_time,
      duration_seconds: row.duration_seconds,
      retries: row.retries,
      result: row.result,
      error: row.error,
    }));
  } finally {
    client.release();
  }
}
