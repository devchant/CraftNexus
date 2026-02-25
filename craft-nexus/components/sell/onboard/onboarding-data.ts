export interface OnboardingSlideData {
  badge: string;
  illustrationAlt: string;
  illustrationSrc: string;
  title: string;
  subtitle: string;
  ctaLabel: string;
}

export const ONBOARDING_SLIDES: OnboardingSlideData[] = [
  {
    badge: "Sell & Learn",
    illustrationAlt: "Artisan crafting pottery",
    illustrationSrc: "/illustration/pottery-artisan.svg",
    title: "Turn Your Craft\nInto Income",
    subtitle: "Sell handmade products and learn\ncreative skills from experts.",
    ctaLabel: "Get Started",
  },
  // Slide 2 placeholder — fill in when implementing issue #32
  {
    badge: "Sell & Learn",
    illustrationAlt: "Artisan showcasing products",
    illustrationSrc: "/illustrations/artisan-showcase.svg",
    title: "Reach Thousands\nOf Buyers",
    subtitle: "List your handmade items and connect\nwith customers worldwide.",
    ctaLabel: "Next",
  },
  // Slide 3 placeholder — fill in when implementing issue #33
  {
    badge: "Sell & Learn",
    illustrationAlt: "Artisan earning income",
    illustrationSrc: "/illustrations/artisan-earning.svg",
    title: "Grow Your\nCraft Business",
    subtitle: "Track sales, manage orders, and\ngrow your creative business.",
    ctaLabel: "Start Selling",
  },
];