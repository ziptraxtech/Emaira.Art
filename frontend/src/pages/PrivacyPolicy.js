import LegalLayout from "./LegalLayout";

const Section = ({ n, title, children }) => (
  <section>
    <h2 className="font-display text-xl md:text-2xl text-[#1A1A18] mb-3">
      {n}. {title}
    </h2>
    <div className="space-y-2">{children}</div>
  </section>
);

const PrivacyPolicy = () => {
  return (
    <LegalLayout title="Privacy Policy" lastUpdated="May 2026">
      <Section n="1" title="Information We Collect">
        <p><strong>Account information:</strong> Name, email, organization, and authentication identifiers from Clerk.</p>
        <p><strong>Usage data:</strong> Page views, inspection uploads, feature interactions, and platform event logs.</p>
        <p><strong>Inspection content:</strong> Site videos, images, design references, project metadata, and the AI-generated analysis tied to them.</p>
        <p><strong>Payment data:</strong> Transaction identifiers from Stripe / Razorpay. We do not store full card numbers on our servers.</p>
      </Section>

      <Section n="2" title="How We Use It">
        <p>To operate and improve the platform, including AI defect detection, safety monitoring, and reality-vs-design analysis.</p>
        <p>To deliver inspection results, share-ready reports, and account notifications.</p>
        <p>To improve our AI models — using anonymized inspection content unless you opt out.</p>
        <p>To respond to support requests and bill you for paid subscriptions.</p>
      </Section>

      <Section n="3" title="Data Sharing">
        <p>We may share data with:</p>
        <ul className="list-disc pl-6 space-y-1">
          <li>AI inference providers (e.g. Google Gemini) for analyzing your inspection videos and images.</li>
          <li>Cloud storage providers (AWS S3, Google Drive) for storing your uploads.</li>
          <li>Payment processors (Stripe, Razorpay) for handling subscriptions.</li>
          <li>Legal authorities when required by law.</li>
        </ul>
        <p>We do not sell your personal data.</p>
      </Section>

      <Section n="4" title="Data Security">
        <p>We use administrative, technical, and physical safeguards — including encrypted transport (HTTPS), encrypted storage at rest, scoped IAM roles, and access logging — to protect your data from unauthorized access.</p>
      </Section>

      <Section n="5" title="Your Rights">
        <p>You may:</p>
        <ul className="list-disc pl-6 space-y-1">
          <li>Access and correct your personal data.</li>
          <li>Request deletion of your account and associated inspection content.</li>
          <li>Export your inspection reports as PDF or JSON.</li>
          <li>Opt out of non-essential communications.</li>
        </ul>
        <p>To exercise any of these rights, contact <a href="mailto:hello@emaira.art" className="text-[#B8962F] hover:underline">hello@emaira.art</a>.</p>
      </Section>

      <Section n="6" title="Policy Changes">
        <p>We may update this Policy from time to time. Notification will be provided via the app or by email. Continued use of the platform after changes take effect means you accept the updated Policy.</p>
      </Section>
    </LegalLayout>
  );
};

export default PrivacyPolicy;
