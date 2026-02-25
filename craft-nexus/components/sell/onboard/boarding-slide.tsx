"use client";

import Image from "next/image";
import { OnboardingSlideData } from "./onboarding-data";

interface OnboardingSlideProps {
  slide: OnboardingSlideData;
  currentIndex: number;
  totalSlides: number;
  onNext: () => void;
  onSkip: () => void;
}

export default function OnboardingSlide({
  slide,
  currentIndex,
  totalSlides,
  onNext,
  onSkip,
}: OnboardingSlideProps) {
  return (
    <div className="onboarding-wrapper">
      {/* Badge */}
      <div className="onboarding-badge">
        <span className="badge-icon" aria-hidden="true">
          {/* Simple circle icon matching Figma */}
            <img
          src='/badgeicon.png'
          alt='Badge Icon'
         
        />
         
        </span>
        <span className="badge-label">{slide.badge}</span>
      </div>

      {/* Illustration */}
      <div className="onboarding-illustration">
        <Image
          src={slide.illustrationSrc}
          alt={slide.illustrationAlt}
          width={260}
          height={260}
          priority
          className="illustration-img"
        />
      </div>

      {/* Text */}
      <div className="onboarding-text">
        <h1 className="onboarding-title">
          {slide.title.split("\n").map((line, i) => (
            <span key={i}>
              {line}
              {i < slide.title.split("\n").length - 1 && <br />}
            </span>
          ))}
        </h1>
        <p className="onboarding-subtitle">
          {slide.subtitle.split("\n").map((line, i) => (
            <span key={i}>
              {line}
              {i < slide.subtitle.split("\n").length - 1 && <br />}
            </span>
          ))}
        </p>
      </div>

      {/* Progress Dots */}
      <div className="onboarding-dots" role="tablist" aria-label="Slide progress">
        {Array.from({ length: totalSlides }).map((_, i) => (
          <span
            key={i}
            role="tab"
            aria-selected={i === currentIndex}
            aria-label={`Slide ${i + 1} of ${totalSlides}`}
            className={`dot ${i === currentIndex ? "dot--active" : ""}`}
          />
        ))}
      </div>

      {/* CTA */}
      <div className="onboarding-cta">
        <button
          className="btn-primary"
          onClick={onNext}
          type="button"
        >
          {slide.ctaLabel}
        </button>
        <button
          className="btn-skip"
          onClick={onSkip}
          type="button"
        >
          Skip
        </button>
      </div>

      <style>{`
        .onboarding-wrapper {
          min-height: 100svh;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 48px 24px 40px;
          background: #ffffff;
          gap: 0;
        }

        /* Badge */
        .onboarding-badge {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 40px;
        }
        .badge-icon {
          display: inline-flex;
          align-items: center;
          justify-content: center;
        }
        .badge-icon img {
          width: 30px;
          height: 30px;
        }
        .badge-label {
          font-family: 'Georgia', serif;
          font-size: 14px;
          color: #5a3e3a;
          letter-spacing: 0.02em;
        }

        /* Illustration */
        .onboarding-illustration {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 100%;
          margin-bottom: 40px;
        }
        .illustration-img {
          width: clamp(180px, 60vw, 260px);
          height: auto;
          object-fit: contain;
        }

        /* Text */
        .onboarding-text {
          text-align: center;
          margin-bottom: 28px;
        }
        .onboarding-title {
          font-family: 'Georgia', serif;
          font-size: clamp(26px, 7vw, 32px);
          font-weight: 700;
          color: #2c1a18;
          line-height: 1.25;
          margin: 0 0 12px;
          letter-spacing: -0.01em;
        }
        .onboarding-subtitle {
          font-family: system-ui, -apple-system, sans-serif;
          font-size: 14px;
          color: #8a7572;
          line-height: 1.6;
          margin: 0;
          max-width: 280px;
        }

        /* Dots */
        .onboarding-dots {
          display: flex;
          gap: 6px;
          margin-bottom: 32px;
        }
        .dot {
          display: block;
          width: 20px;
          height: 4px;
          border-radius: 2px;
          background: #e0d0ce;
          transition: background 0.2s;
        }
        .dot--active {
          background: #b07c76;
        }

        /* CTA */
        .onboarding-cta {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 14px;
          width: 100%;
          max-width: 320px;
        }
        .btn-primary {
          width: 100%;
          padding: 15px 24px;
          background: #C4928F;
          color: #ffffff;
          border: none;
          border-radius: 16px;
          font-family: system-ui, -apple-system, sans-serif;
          font-size: 15px;
          font-weight: 600;
          cursor: pointer;
          transition: background 0.18s, transform 0.1s;
          letter-spacing: 0.01em;
        }
        .btn-primary:hover {
          background: #9c6b65;
        }
        .btn-primary:active {
          transform: scale(0.98);
        }
        .btn-skip {
          background: none;
          border: none;
          color: #8a7572;
          font-family: system-ui, -apple-system, sans-serif;
          font-size: 14px;
          cursor: pointer;
          padding: 4px 12px;
          transition: color 0.15s;
        }
        .btn-skip:hover {
          color: #5a3e3a;
        }

        /* Responsive */
        @media (min-width: 480px) {
          .onboarding-wrapper {
            padding: 64px 32px 48px;
          }
        }
        @media (min-width: 768px) {
          .onboarding-wrapper {
            max-width: 420px;
            margin: 0 auto;
            min-height: 100vh;
          }
        }
      `}</style>
    </div>
  );
}