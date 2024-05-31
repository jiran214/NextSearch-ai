import Link from "next/link"
import { CircleUser, Menu, Package2, Search } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"


export function DashboardLayoutUI(props){
    return (
        <div className="flex min-h-screen w-full flex-col">
            <header className="sticky top-0 flex h-16 items-center gap-4 border-b bg-background px-4 md:px-6">
            <nav className="hidden flex-col gap-6 text-lg font-medium md:flex md:flex-row md:items-center md:gap-5 md:text-sm lg:gap-6 text-nowrap">
                <Link
                href="#"
                className="flex items-center gap-2 text-lg font-semibold md:text-base"
                >
                <Package2 className="h-6 w-6" />
                <span className="sr-only">Acme Inc</span>
                </Link>
                <Link
                href="/"
                className="text-muted-foreground transition-colors hover:text-foreground"
                >
                主页
                </Link>
                <Link
                href="/explore"
                className="text-muted-foreground transition-colors hover:text-foreground"
                >
                发现
                </Link>
                <Link
                href="/history"
                className="text-muted-foreground transition-colors hover:text-foreground"
                >
                历史
                </Link>
                <Link
                href="/settings"
                className="text-muted-foreground transition-colors hover:text-foreground"
                >
                设置
                </Link>
            </nav>
            <Sheet>
                <SheetTrigger asChild>
                <Button
                    variant="outline"
                    size="icon"
                    className="shrink-0 md:hidden"
                >
                    <Menu className="h-5 w-5" />
                    <span className="sr-only">Toggle navigation menu</span>
                </Button>
                </SheetTrigger>
                <SheetContent side="left">
                <nav className="grid gap-6 text-lg font-medium">
                    <Link
                    href="#"
                    className="flex items-center gap-2 text-lg font-semibold"
                    >
                    <Package2 className="h-6 w-6" />
                    <span className="sr-only">Acme Inc</span>
                    </Link>
                    <Link
                    href="#"
                    className="text-muted-foreground hover:text-foreground"
                    >
                    主页
                    </Link>
                    <Link
                    href="#"
                    className="text-muted-foreground hover:text-foreground"
                    >
                    发现
                    </Link>
                    <Link
                    href="#"
                    className="text-muted-foreground hover:text-foreground"
                    >
                    历史
                    </Link>
                    <Link href="#" className="hover:text-foreground">
                    设置
                    </Link>
                </nav>
                </SheetContent>
            </Sheet>
            <div className="flex w-full items-center gap-4 md:ml-auto md:gap-2 lg:gap-4">
                <form className="ml-auto flex-1 sm:flex-initial">
                <div className="relative"></div>
                </form>
                <DropdownMenu>
                <DropdownMenuTrigger asChild>
                    <Button variant="secondary" size="icon" className="rounded-full">
                    <CircleUser className="h-5 w-5" />
                    <span className="sr-only">Toggle user menu</span>
                    </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                    <DropdownMenuLabel>My Account</DropdownMenuLabel>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem>Settings</DropdownMenuItem>
                    <DropdownMenuItem>Support</DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem>Logout</DropdownMenuItem>
                </DropdownMenuContent>
                </DropdownMenu>
            </div>
            </header>
            <main>{props.children}</main>
        </div>
    )
}