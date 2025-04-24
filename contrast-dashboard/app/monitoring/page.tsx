import { AppSidebar } from "../../components/app-sidebar"
import { ScraperLibraryTable } from "@/components/scraper-library-table"
import { SiteHeader } from "../../components/site-header"
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar"

// Dummy scraper library data
const dummyScraperLibrary = [
  {
    id: "1",
    name: "contrast_product_scraper",
    health: "healthy",
    lastRan: new Date(Date.now() - 2 * 60 * 60 * 1000),
    lastModified: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
  },
  {
    id: "2",
    name: "contrast_category_scraper",
    health: "healthy",
    lastRan: new Date(Date.now() - 8 * 60 * 60 * 1000),
    lastModified: new Date(Date.now() - 45 * 24 * 60 * 60 * 1000),
  },
  {
    id: "3",
    name: "contrast_price_scraper",
    health: "warning",
    lastRan: new Date(Date.now() - 12 * 60 * 60 * 1000),
    lastModified: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000),
  },
  {
    id: "4",
    name: "contrast_inventory_scraper",
    health: "healthy",
    lastRan: new Date(Date.now() - 24 * 60 * 60 * 1000),
    lastModified: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000),
  },
  {
    id: "5",
    name: "contrast_image_scraper",
    health: "broken",
    lastRan: new Date(Date.now() - 26 * 60 * 60 * 1000),
    lastModified: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000),
  },
  {
    id: "6",
    name: "contrast_review_scraper",
    health: "healthy",
    lastRan: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
    lastModified: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000),
  },
  {
    id: "7",
    name: "contrast_availability_scraper",
    health: "warning",
    lastRan: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000),
    lastModified: new Date(Date.now() - 25 * 24 * 60 * 60 * 1000),
  },
  {
    id: "8",
    name: "contrast_promotion_scraper",
    health: "healthy",
    lastRan: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
    lastModified: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
  },
  {
    id: "9",
    name: "contrast_shipping_scraper",
    health: "healthy",
    lastRan: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
    lastModified: new Date(Date.now() - 40 * 24 * 60 * 60 * 1000),
  },
  {
    id: "10",
    name: "contrast_competitor_scraper",
    health: "broken",
    lastRan: null,
    lastModified: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
  },
  {
    id: "11",
    name: "contrast_metadata_scraper",
    health: "healthy",
    lastRan: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000),
    lastModified: new Date(Date.now() - 35 * 24 * 60 * 60 * 1000),
  },
  {
    id: "12",
    name: "contrast_seo_scraper",
    health: "warning",
    lastRan: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
    lastModified: new Date(Date.now() - 50 * 24 * 60 * 60 * 1000),
  },
]

export default function MonitoringPage() {
  return (
    <SidebarProvider>
      <AppSidebar variant="inset" />
      <SidebarInset>
        <SiteHeader title="Monitoring Station" />
        <div className="flex flex-1 flex-col">
          <div className="@container/main flex flex-1 flex-col gap-2">
            <div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
              <ScraperLibraryTable data={dummyScraperLibrary} />
            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
