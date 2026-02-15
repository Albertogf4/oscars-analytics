import { motion } from 'framer-motion';
import { Layout } from '../components/Layout';
import { TemplateUploader } from '../components/TemplateUploader';
import { TemplateManager } from '../components/TemplateManager';

export function TemplatesPage() {
  return (
    <Layout>
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h2 className="text-4xl font-semibold tracking-tight text-text-primary mb-2">
          Template Studio
        </h2>
        <p className="text-text-secondary max-w-2xl">
          Add new meme templates to the generation pipeline. Upload an image and our AI agents
          will analyze its visual structure, detect text slots, and understand the irony mechanics
          to create a fully functional template.
        </p>
      </motion.div>

      {/* Template Uploader */}
      <TemplateUploader />

      {/* Template Manager */}
      <TemplateManager />
    </Layout>
  );
}
