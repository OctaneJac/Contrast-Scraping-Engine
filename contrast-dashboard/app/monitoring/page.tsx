"use client"
import { AppSidebar } from "../../components/app-sidebar"
import { ScraperLibraryTable } from "@/components/scraper-library-table"
import { SiteHeader } from "../../components/site-header"
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar"
// import { getScraperLibrary } from "@/lib/getScraperLibrary";
import { useEffect, useState } from "react"


export default function MonitoringPage() {
  const [data, setData] = useState([])

  useEffect(() => {
    fetch("/api/scraperlibrary")
      .then(res => res.json())
      .then(setData)
  }, [])

  return (
    <SidebarProvider>
      <AppSidebar variant="inset" />
      <SidebarInset>
        <SiteHeader title="Monitoring Station" />
        <div className="flex flex-1 flex-col">
          <div className="@container/main flex flex-1 flex-col gap-2">
            <div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
              <ScraperLibraryTable data={data} />
            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
