// lib/getScrapingStats.ts
import pool from "./db";

export async function getScrapingStats() {
  const client = await pool.connect();

  try {
    const stats = {
      totalProducts: 0,
      activeProducts: 0,
      lastScraped: null,
      lastPriceUpdate: null,
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

    // Assuming latest price update correlates with spider end time
    const lastPriceUpdateResult = await client.query(`
      SELECT MAX(end_time) AS last_price_update
      FROM spider_logs
      WHERE scraper_name ILIKE '%validation%' AND result = 'success'
    `);
    stats.lastPriceUpdate = lastPriceUpdateResult.rows[0].last_price_update;

    return stats;
  } finally {
    client.release();
  }
}
