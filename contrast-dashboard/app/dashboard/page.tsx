import { AppSidebar } from "@/components/app-sidebar"
import { DashboardStats } from "@/components/dashboard-stats"
import { ScraperHistoryTable } from "@/components/scraper-history-table"
import { SiteHeader } from "@/components/site-header"
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar"
import { getScrapingStats } from "@/lib/getScrapingStats";
import { getScrapingHistory } from "@/lib/getScrapingHistory";

export default async function Page() {
  // In a real application, you would fetch this data from the database
  // const stats = await getScrapingStats();
  // const scraperHistory = await getScraperHistory();

  // For preview, use the dummy data
  const stats = await getScrapingStats();
  const scraperHistory = await getScrapingHistory();

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
