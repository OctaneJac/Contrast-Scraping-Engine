import pool from "./db";

interface ScrapingHistoryRow {
  scraper_name: string;
  celery_trigger_time: Date;
  actual_start_time: Date;
  end_time: Date;
  duration_seconds: number;
  retries: number;
  result: string;
  Terminal_Notes: string | null;
}

export async function getScrapingHistory() {
  const client = await pool.connect();

  try {
    const result = await client.query<ScrapingHistoryRow>(`
      SELECT 
        scraper_name,
        celery_trigger_time,
        actual_start_time,
        end_time,
        duration_seconds,
        retries,
        result,
        Terminal_Notes
      FROM spider_logs
      ORDER BY celery_trigger_time DESC
      LIMIT 100
    `) as { rows: ScrapingHistoryRow[] };

    return result.rows.map((row) => ({
      scraper_name: row.scraper_name,
      celery_trigger_time: row.celery_trigger_time,
      actual_start_time: row.actual_start_time,
      end_time: row.end_time,
      duration_seconds: row.duration_seconds,
      retries: row.retries,
      result: row.result,
      error: row.Terminal_Notes,
    }));
  } finally {
    client.release();
  }
}