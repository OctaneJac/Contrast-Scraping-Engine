// lib/getScraperLibrary.ts
import pool from "./db";

interface ScraperRow {
  id: number;
  name: string;
  status: string;
  last_modified: Date;
  last_ran: Date ;
}

export async function getScraperLibrary() {
  const client = await pool.connect();

  try {
    const result = await client.query<ScraperRow>(`
      SELECT 
        id,
        name,
        status,
        last_modified,
        last_ran
      FROM listofscrapers
      ORDER BY last_ran DESC
    `) as { rows: ScraperRow[] };

    return result.rows.map((row) => ({
      id: row.id.toString(),
      name: row.name,
      health: row.status,
      lastModified: row.last_modified,
      lastRan: row.last_ran,
    }));
  } finally {
    client.release();
  }
}
