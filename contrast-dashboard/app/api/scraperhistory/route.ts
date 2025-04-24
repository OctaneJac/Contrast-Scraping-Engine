import { NextResponse } from "next/server"
import { getScrapingHistory } from "@/lib/getScrapingHistory"

export async function GET() {
  const data = await getScrapingHistory()
  return NextResponse.json(data)
}
