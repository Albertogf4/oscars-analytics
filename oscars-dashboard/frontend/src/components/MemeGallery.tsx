import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useMemes } from '../hooks/useMemes';
import type { GeneratedMeme } from '../types/memes';

const API_BASE = 'http://localhost:8000';

type TabType = 'all' | 'pro_obaa' | 'anti_sinners';

interface MemeGalleryProps {
  lastGeneratedIds?: Set<string>;
}

export function MemeGallery({ lastGeneratedIds = new Set() }: MemeGalleryProps) {
  const [activeTab, setActiveTab] = useState<TabType>('all');
  const [selectedMeme, setSelectedMeme] = useState<GeneratedMeme | null>(null);

  const { data, isLoading, error } = useMemes();

  const filteredMemes = data?.memes.filter((meme) =>
    activeTab === 'all' ? true : meme.category === activeTab
  ) ?? [];

  const getMemeUrl = (meme: GeneratedMeme) => `${API_BASE}${meme.url}`;

  const getMemeTitle = (meme: GeneratedMeme) => {
    // Generate a nice title from template_id
    return meme.template_id
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  if (isLoading) {
    return (
      <section className="mt-16">
        <div className="flex items-center justify-center py-12">
          <div className="inline-block w-6 h-6 border-2 border-text-muted border-t-accent-gold rounded-full animate-spin" />
          <span className="ml-3 text-text-secondary">Loading memes...</span>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="mt-16">
        <div className="text-center py-12">
          <p className="text-accent-red">Failed to load memes</p>
          <p className="text-text-muted text-sm mt-2">{(error as Error).message}</p>
        </div>
      </section>
    );
  }

  return (
    <section className="mt-16">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-sm font-medium text-text-muted uppercase tracking-wide">
            Meme Campaign
          </h3>
          <p className="text-text-secondary text-sm mt-1">
            Sentiment-powered memes for Oscar season
            {data && (
              <span className="text-text-muted ml-2">
                ({data.total} total)
              </span>
            )}
          </p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2">
          {[
            { key: 'all', label: 'All' },
            { key: 'pro_obaa', label: `Pro OBAA (${data?.categories.pro_obaa ?? 0})` },
            { key: 'anti_sinners', label: `Anti Sinners (${data?.categories.anti_sinners ?? 0})` },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as TabType)}
              className={`px-4 py-2 text-sm font-medium rounded transition-colors ${
                activeTab === tab.key
                  ? 'bg-accent-gold text-bg-primary'
                  : 'bg-bg-card text-text-secondary hover:text-text-primary'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Meme Grid */}
      {filteredMemes.length === 0 ? (
        <div className="text-center py-12 card">
          <p className="text-text-secondary">No memes found</p>
          <p className="text-text-muted text-sm mt-2">
            Generate some memes using the generator below
          </p>
        </div>
      ) : (
        <motion.div
          layout
          className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4"
        >
          <AnimatePresence mode="popLayout">
            {filteredMemes.map((meme) => (
              <motion.div
                key={meme.id}
                layout
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.2 }}
                className="card p-2 cursor-pointer hover-lift group relative"
                onClick={() => setSelectedMeme(meme)}
              >
                {/* NEW Badge */}
                {lastGeneratedIds.has(meme.id) && (
                  <motion.span
                    initial={{ scale: 0, rotate: -12 }}
                    animate={{ scale: 1, rotate: -12 }}
                    className="absolute top-3 right-3 z-10 px-2 py-0.5 bg-accent-gold text-bg-primary text-xs font-bold rounded-full shadow-lg"
                  >
                    NEW
                  </motion.span>
                )}
                <div className="aspect-square overflow-hidden rounded bg-bg-secondary">
                  <img
                    src={getMemeUrl(meme)}
                    alt={getMemeTitle(meme)}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    loading="lazy"
                  />
                </div>
                <div className="mt-2 px-1">
                  <p className="text-xs text-text-secondary truncate">{getMemeTitle(meme)}</p>
                  <span
                    className={`inline-block mt-1 px-2 py-0.5 text-xs rounded ${
                      meme.category === 'pro_obaa'
                        ? 'bg-accent-green/10 text-accent-green'
                        : 'bg-accent-red/10 text-accent-red'
                    }`}
                  >
                    {meme.category === 'pro_obaa' ? 'Pro OBAA' : 'Anti Sinners'}
                  </span>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </motion.div>
      )}

      {/* Lightbox Modal */}
      <AnimatePresence>
        {selectedMeme && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 p-4"
            onClick={() => setSelectedMeme(null)}
          >
            <motion.div
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.9 }}
              className="relative max-w-3xl max-h-[90vh] w-full"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Close button */}
              <button
                onClick={() => setSelectedMeme(null)}
                className="absolute -top-10 right-0 text-text-secondary hover:text-text-primary"
              >
                Close
              </button>

              {/* Image */}
              <img
                src={getMemeUrl(selectedMeme)}
                alt={getMemeTitle(selectedMeme)}
                className="w-full h-auto rounded-lg"
              />

              {/* Info */}
              <div className="mt-4 flex items-center justify-between">
                <div>
                  <h4 className="text-lg font-medium text-text-primary">
                    {getMemeTitle(selectedMeme)}
                  </h4>
                  <div className="flex items-center gap-2 mt-1">
                    <span
                      className={`inline-block px-2 py-0.5 text-xs rounded ${
                        selectedMeme.category === 'pro_obaa'
                          ? 'bg-accent-green/10 text-accent-green'
                          : 'bg-accent-red/10 text-accent-red'
                      }`}
                    >
                      {selectedMeme.category === 'pro_obaa' ? 'Boost OBAA' : 'Counter Sinners'}
                    </span>
                    <span className="text-xs text-text-muted">
                      Template: {selectedMeme.template_id}
                    </span>
                  </div>
                </div>

                {/* Download button */}
                <a
                  href={getMemeUrl(selectedMeme)}
                  download={selectedMeme.filename}
                  className="px-4 py-2 bg-accent-gold text-bg-primary text-sm font-medium rounded hover:bg-accent-gold/90 transition-colors"
                >
                  Download
                </a>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  );
}
