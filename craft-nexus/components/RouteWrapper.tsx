"use client";

import { usePathname } from "next/navigation";
import { Navigation } from "@/components/organisms/Navigation";
import Footer from "@/components/organisms/footer";
import { useMemo, memo } from "react";

interface RouteWrapperProps {
  children: React.ReactNode;
}

/**
 * RouteWrapper - Conditionally renders Navigation and Footer based on the current route
 * Hides header/footer on onboarding routes for a cleaner user experience
 */
function RouteWrapperComponent({ children }: RouteWrapperProps) {
  const pathname = usePathname();
  
  // Routes where navigation and footer should be hidden
  const isOnboardingRoute = useMemo(() => 
    pathname.startsWith("/sell/onboarding"), 
    [pathname]
  );
  
  return (
    <>
      {!isOnboardingRoute && <Navigation />}
      {children}
      {!isOnboardingRoute && <Footer />}
    </>
  );
}

// Memoize to prevent unnecessary re-renders
const RouteWrapper = memo(RouteWrapperComponent);
RouteWrapper.displayName = "RouteWrapper";

export default RouteWrapper;
