import LegalLayout from "./LegalLayout";

const Section = ({ n, title, children }) => (
  <section>
    <h2 className="font-display text-xl md:text-2xl text-[#1A1A18] mb-3">
      {n}. {title}
    </h2>
    <div className="space-y-2">{children}</div>
  </section>
);

const TermsOfUse = () => {
  return (
    <LegalLayout title="Terms of Use" lastUpdated="May 2026">
      <Section n="1" title="Acceptance of Terms">
        <p>By accessing or using Emaira, you agree to be bound by these Terms of Use. If you do not agree, do not use the platform.</p>
      </Section>

      <Section n="2" title="Account & Eligibility">
        <p>You must be at least 18 years old and provide accurate information when creating an account. You are responsible for all activity that occurs under your account.</p>
      </Section>

      <Section n="3" title="Acceptable Use">
        <p>You agree not to:</p>
        <ul className="list-disc pl-6 space-y-1">
          <li>Upload content you do not have the right to use or that violates any law.</li>
          <li>Reverse-engineer, scrape, or attempt to extract our AI models.</li>
          <li>Use the platform to harm, harass, or defame others.</li>
          <li>Resell or sublicense the service without written permission.</li>
        </ul>
      </Section>

      <Section n="4" title="AI Output Disclaimer">
        <p>Emaira's defect detection, safety monitoring, and design-validation results are AI-generated and intended as decision support — not a substitute for licensed professional engineering judgment. You remain responsible for verifying findings before acting on them.</p>
      </Section>

      <Section n="5" title="Your Content">
        <p>You retain ownership of the videos, images, and metadata you upload. By uploading, you grant Emaira a limited license to process that content for the purpose of delivering the service and improving our AI models (subject to the Privacy Policy).</p>
      </Section>

      <Section n="6" title="Service Availability">
        <p>We aim for high availability but do not guarantee uninterrupted service. Maintenance, updates, or third-party outages may cause temporary unavailability.</p>
      </Section>

      <Section n="7" title="Limitation of Liability">
        <p>To the maximum extent permitted by law, Emaira and its affiliates are not liable for any indirect, incidental, special, or consequential damages arising out of your use of the platform.</p>
      </Section>

      <Section n="8" title="Changes to Terms">
        <p>We may update these Terms from time to time. Material changes will be communicated via the app or by email. Continued use after the effective date means you accept the updated Terms.</p>
      </Section>

      <Section n="9" title="Contact">
        <p>
          Questions? Reach us at{" "}
          <a href="mailto:hello@emaira.art" className="text-[#B8962F] hover:underline">
            hello@emaira.art
          </a>
          .
        </p>
      </Section>
    </LegalLayout>
  );
};

export default TermsOfUse;
