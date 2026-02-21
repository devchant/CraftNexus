import FeatureBar from "@/components/organisms/FeatureBar";
import HeroSection from "@/components/organisms/HomepageHero";
import TestimonialsSection from "@/components/organisms/Testimonials";

export default function Home() {
  return (
    <div className="">
      <HeroSection />
      <FeatureBar/>
      <TestimonialsSection />
    </div>

  );
}
