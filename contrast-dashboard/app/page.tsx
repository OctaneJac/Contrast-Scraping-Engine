import Image from "next/image";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8 ">
      <h1 className="text-5xl font-bold text-center mb-6 tracking-tight">
        Welcome to the Contrast Admin Dashboard.
      </h1>
      <Button asChild>
       <Link href="/dashboard">Access Dashboard</Link>
      </Button>
    </div>
  );
}
