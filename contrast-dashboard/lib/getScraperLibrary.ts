// lib/getScraperLibrary.ts
import pool from "./db";

export async function getScraperLibrary() {
  const client = await pool.connect();

  try {
    const result = await client.query(`
      SELECT 
        id,
        name,
        status,
        last_modified,
        last_ran
      FROM listofscrapers
      ORDER BY last_ran DESC
    `);

    return result.rows.map((row: any) => ({
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

// // Map database status to UI health badge
// function mapStatusToHealth(status: string) {
//   switch (status.toLowerCase()) {
//     case "running":
//     case "healthy":
//       return "healthy";
//     case "warning":
//     case "degraded":
//       return "warning";
//     case "offline":
//     case "error":
//     default:
//       return "error";
//   }
// }
