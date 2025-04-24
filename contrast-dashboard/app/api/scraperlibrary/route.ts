import { NextResponse } from 'next/server'
import { getScraperLibrary } from '@/lib/getScraperLibrary'

export async function GET() {
  const data = await getScraperLibrary()
  return NextResponse.json(data)
}