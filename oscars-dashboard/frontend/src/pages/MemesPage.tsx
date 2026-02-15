import { useState } from 'react';
import { Layout } from '../components/Layout';
import { MemeGallery } from '../components/MemeGallery';
import { MemeGenerator } from '../components/MemeGenerator';
import { motion } from 'framer-motion';

export function MemesPage() {
  const [lastGeneratedIds, setLastGeneratedIds] = useState<Set<string>>(new Set());

  const handleGenerated = (memeIds: string[]) => {
    setLastGeneratedIds(new Set(memeIds));
  };

  return (
    <Layout>
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-12"
      >
        <div className="flex items-baseline gap-4 mb-2">
          <h2 className="text-4xl font-semibold tracking-tight text-text-primary">
            Meme Studio
          </h2>
          {lastGeneratedIds.size > 0 && (
            <span className="text-sm text-accent-gold">
              {lastGeneratedIds.size} new memes generated
            </span>
          )}
        </div>
        <p className="text-text-secondary max-w-2xl">
          Generate AI-powered memes based on real sentiment analysis from movie discussions.
          Pro-OBAA memes boost One Battle After Another, Anti-Sinners memes mock the competition.
        </p>
      </motion.div>

      {/* Meme Gallery */}
      <MemeGallery lastGeneratedIds={lastGeneratedIds} />

      {/* Meme Generator */}
      <MemeGenerator onGenerated={handleGenerated} />
    </Layout>
  );
}
