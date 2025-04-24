import { AppSidebar } from "@/components/app-sidebar"
import { DashboardStats } from "@/components/dashboard-stats"
import { ScraperHistoryTable } from "@/components/scraper-history-table"
import { SiteHeader } from "@/components/site-header"
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar"

// Hardcoded dummy values for preview
const dummyStats = {
  lastScraped: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
  lastPriceUpdate: new Date(Date.now() - 4 * 60 * 60 * 1000), // 4 hours ago
  totalProducts: 12458,
  activeProducts: 9873,
}

// Dummy scraper history data
const dummyScraperHistory = [
  {
    scraper_name: "contrast_product_scraper",
    celery_trigger_time: new Date(Date.now() - 2 * 60 * 60 * 1000),
    actual_start_time: new Date(Date.now() - 2 * 60 * 60 * 1000 + 30000),
    end_time: new Date(Date.now() - 2 * 60 * 60 * 1000 + 15 * 60 * 1000),
    duration_seconds: 870,
    retries: 0,
    result: "Success - 245 products scraped",
    error: null,
  },
  {
    scraper_name: "contrast_category_scraper",
    celery_trigger_time: new Date(Date.now() - 8 * 60 * 60 * 1000),
    actual_start_time: new Date(Date.now() - 8 * 60 * 60 * 1000 + 45000),
    end_time: new Date(Date.now() - 8 * 60 * 60 * 1000 + 10 * 60 * 1000),
    duration_seconds: 555,
    retries: 0,
    result: "Success - 32 categories updated",
    error: null,
  },
  {
    scraper_name: "contrast_price_scraper",
    celery_trigger_time: new Date(Date.now() - 12 * 60 * 60 * 1000),
    actual_start_time: new Date(Date.now() - 12 * 60 * 60 * 1000 + 20000),
    end_time: new Date(Date.now() - 12 * 60 * 60 * 1000 + 45 * 60 * 1000),
    duration_seconds: 2680,
    retries: 2,
    result: "Partial success - 1890/2000 prices updated",
    error: "Timeout on 110 requests",
  },
  {
    scraper_name: "contrast_inventory_scraper",
    celery_trigger_time: new Date(Date.now() - 24 * 60 * 60 * 1000),
    actual_start_time: new Date(Date.now() - 24 * 60 * 60 * 1000 + 15000),
    end_time: new Date(Date.now() - 24 * 60 * 60 * 1000 + 30 * 60 * 1000),
    duration_seconds: 1785,
    retries: 1,
    result: "Success - 1245 inventory records updated",
    error: null,
  },
  {
    scraper_name: "contrast_product_scraper",
    celery_trigger_time: new Date(Date.now() - 26 * 60 * 60 * 1000),
    actual_start_time: new Date(Date.now() - 26 * 60 * 60 * 1000 + 25000),
    end_time: null,
    duration_seconds: null,
    retries: 3,
    result: null,
    error: "Connection refused after 3 retries",
  },
]

export default async function Page() {
  // In a real application, you would fetch this data from the database
  // const stats = await getScrapingStats();
  // const scraperHistory = await getScraperHistory();

  // For preview, use the dummy data
  const stats = dummyStats
  const scraperHistory = dummyScraperHistory

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
