import type { NextApiRequest, NextApiResponse } from "next";
import { Pool } from "pg";

const pool = new Pool({
  connectionString: process.env.POSTGRES_URI, // Set this in your .env.local
});

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    // Get last scraped time from spider_logs
    const spiderLogsResult = await pool.query(
      `SELECT MAX(actual_start_time) AS last_scraped FROM spider_logs`
    );
    const lastScraped = spiderLogsResult.rows[0]?.last_scraped;

    // Get last price update from products
    const lastPriceUpdateResult = await pool.query(
      `SELECT MAX(created_at) AS last_price_update FROM products`
    );
    const lastPriceUpdate = lastPriceUpdateResult.rows[0]?.last_price_update;

    // Get total and active products
    const totalProductsResult = await pool.query(
      `SELECT COUNT(*) AS total FROM products`
    );
    const activeProductsResult = await pool.query(
      `SELECT COUNT(*) AS active FROM products WHERE is_active = true`
    );

    res.status(200).json({
      lastScraped,
      lastPriceUpdate,
      totalProducts: parseInt(totalProductsResult.rows[0]?.total ?? "0", 10),
      activeProducts: parseInt(activeProductsResult.rows[0]?.active ?? "0", 10),
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Failed to fetch dashboard stats" });
  }
}