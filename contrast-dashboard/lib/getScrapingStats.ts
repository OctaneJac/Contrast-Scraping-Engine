// lib/getScrapingStats.ts
import pool from "./db";

export async function getScrapingStats() {
  const client = await pool.connect();

  try {
    const stats = {
      totalProducts: 0,
      activeProducts: 0,
      lastScraped: null,
      totalScrapes: 0,
    };

    const productCounts = await client.query(`
      SELECT 
        COUNT(*) AS total,
        COUNT(*) FILTER (WHERE is_active = true) AS active
      FROM products
    `);
    stats.totalProducts = parseInt(productCounts.rows[0].total);
    stats.activeProducts = parseInt(productCounts.rows[0].active);

    const lastScrapedResult = await client.query(`
      SELECT MAX(end_time) AS last_scraped
      FROM spider_logs
      WHERE result = 'success'
    `);
    stats.lastScraped = lastScrapedResult.rows[0].last_scraped;

    const totalScrapesResult = await client.query(`
      SELECT COUNT(*) AS total_scrapes
      FROM spider_logs
    `);
    stats.totalScrapes = parseInt(totalScrapesResult.rows[0].total_scrapes);

    return stats;
  } finally {
    client.release();
  }
}
