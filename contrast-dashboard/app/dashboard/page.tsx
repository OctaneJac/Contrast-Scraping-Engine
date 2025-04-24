"use client"
import { AppSidebar } from "@/components/app-sidebar"
import { DashboardStats } from "@/components/dashboard-stats"
import { ScraperHistoryTable } from "@/components/scraper-history-table"
import { SiteHeader } from "@/components/site-header"
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar"
// import { getScrapingStats } from "@/lib/getScrapingStats";
// import { getScrapingHistory } from "@/lib/getScrapingHistory";
import { useEffect, useState } from "react"


interface Stats {
  lastScraped: Date
  lastPriceUpdate: Date
  totalProducts: number
  activeProducts: number
}

export default function Page() {
  const [stats, setStats] = useState<Stats>({
    lastScraped: new Date(),
    lastPriceUpdate: new Date(),
    totalProducts: 0,
    activeProducts: 0,
  })
  const [scraperHistory, setScraperHistory] = useState([])

  useEffect(() => {
    fetch("/api/scraperstats")
      .then(res => res.json())
      .then(data => setStats(data))

    fetch("/api/scraperhistory")
      .then(res => res.json())
      .then(setScraperHistory)
  }, [])
  
  return (
    <SidebarProvider>
      <AppSidebar variant="inset" />
      <SidebarInset>
        <SiteHeader />
        <div className="flex flex-1 flex-col">
          <div className="@container/main flex flex-1 flex-col gap-2">
            <div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
              <DashboardStats
                lastScraped={stats.lastScraped}
                lastPriceUpdate={stats.lastPriceUpdate}
                totalProducts={stats.totalProducts}
                activeProducts={stats.activeProducts}
              />
              <ScraperHistoryTable data={scraperHistory} />
            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
