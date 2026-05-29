import LegalLayout from "./LegalLayout";

const Section = ({ n, title, children }) => (
  <section>
    <h2 className="font-display text-xl md:text-2xl text-[#1A1A18] mb-3">
      {n}. {title}
    </h2>
    <div className="space-y-2">{children}</div>
  </section>
);

const RefundPolicy = () => {
  return (
    <LegalLayout title="Refund & Cancellation Policy" lastUpdated="May 2026">
      <Section n="1" title="Software Subscriptions">
        <p>Monthly subscriptions are non-refundable after the billing date. You may cancel at any time and retain access until the end of the current billing period.</p>
        <p>Annual subscriptions may be canceled within 14 days of purchase for a full refund.</p>
        <p>No refunds are issued after the 14-day period.</p>
      </Section>

      <Section n="2" title="One-time Purchases & Add-ons">
        <p>Pay-as-you-go inspection credits and one-time analysis add-ons are non-refundable once consumed.</p>
        <p>Unused credits may be refunded within 7 days of purchase, minus a processing fee.</p>
      </Section>

      <Section n="3" title="Renewal Policy">
        <p>Subscription renewals are automatic. To avoid renewal, cancel at least 7 days before your expiry date from your account settings or by emailing support.</p>
      </Section>

      <Section n="4" title="How to Request">
        <p>
          To request a refund or cancellation, contact support at{" "}
          <a href="mailto:hello@emaira.art" className="text-[#B8962F] hover:underline">
            hello@emaira.art
          </a>{" "}
          with your account email and subscription ID. We respond to refund requests within 5 business days.
        </p>
      </Section>
    </LegalLayout>
  );
};

export default RefundPolicy;
