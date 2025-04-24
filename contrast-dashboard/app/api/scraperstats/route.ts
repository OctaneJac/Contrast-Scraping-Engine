import { NextResponse } from "next/server"
import { getScrapingStats } from "@/lib/getScrapingStats"

export async function GET() {
  const data = await getScrapingStats()
  // const stats = {
  //   lastScraped: data.lastScraped,
  //   lastPriceUpdate: data.lastPriceUpdate,
  //   totalProducts: data.totalProducts,
  //   activeProducts: data.activeProducts
  // }

  return NextResponse.json(data)
}

