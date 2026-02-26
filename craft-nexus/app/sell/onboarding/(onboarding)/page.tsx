"use client";

import OnboardingSlide from "@/components/sell/onboard/boarding-slide";
import { ONBOARDING_SLIDES } from "@/components/sell/onboard/onboarding-data";
import { useRouter } from "next/navigation";

/**
 * Sell Onboarding Page - First slide
 * Guides new sellers through the platform introduction
 */
export default function SellOnboardingPage() {
  const router = useRouter();

  const handleGetStarted = () => {
    router.push("/sell/onboarding/2");
  };

  const handleSkip = () => {
    router.push("/sell/dashboard");
  };

  return (
    <OnboardingSlide
      slide={ONBOARDING_SLIDES[0]}
      currentIndex={0}
      totalSlides={ONBOARDING_SLIDES.length}
      onNext={handleGetStarted}
      onSkip={handleSkip}
    />
  );
}
