import { useState } from 'react';
import { motion } from 'framer-motion';
import { useGenerateMemes, useMemeTemplates } from '../hooks/useMemes';
import type { GenerateRequest } from '../types/memes';

type Category = 'pro_obaa' | 'anti_sinners';
type Tone = 'savage' | 'playful' | 'sarcastic';

interface MemeGeneratorProps {
  onGenerated?: (memeIds: string[]) => void;
}

export function MemeGenerator({ onGenerated }: MemeGeneratorProps) {
  const [category, setCategory] = useState<Category>('pro_obaa');
  const [selectedTemplates, setSelectedTemplates] = useState<string[]>([]);
  const [numMemes, setNumMemes] = useState(5);
  const [tone, setTone] = useState<Tone>('sarcastic');

  const { data: templatesData } = useMemeTemplates();
  const generateMutation = useGenerateMemes();

  const handleTemplateToggle = (templateId: string) => {
    setSelectedTemplates((prev) =>
      prev.includes(templateId)
        ? prev.filter((t) => t !== templateId)
        : [...prev, templateId]
    );
  };

  const handleSelectAll = () => {
    if (selectedTemplates.length === templatesData?.templates.length) {
      setSelectedTemplates([]);
    } else {
      setSelectedTemplates(templatesData?.templates.map((t) => t.id) ?? []);
    }
  };

  const handleGenerate = () => {
    const request: GenerateRequest = {
      category,
      templates: selectedTemplates.length > 0 ? selectedTemplates : undefined,
      num_memes: numMemes,
      tone,
    };
    generateMutation.mutate(request, {
      onSuccess: (data) => {
        onGenerated?.(data.memes.map((m) => m.id));
      },
    });
  };

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-8 card"
    >
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-text-primary">
            Generate New Memes
          </h3>
          <p className="text-sm text-text-secondary mt-1">
            Create AI-powered memes based on sentiment analysis
          </p>
        </div>
      </div>

      <div className="space-y-6">
        {/* Campaign Category */}
        <div>
          <label className="block text-sm font-medium text-text-secondary mb-2">
            Campaign
          </label>
          <div className="flex gap-3">
            <button
              onClick={() => setCategory('pro_obaa')}
              className={`flex-1 py-3 px-4 rounded-lg text-sm font-medium transition-colors ${
                category === 'pro_obaa'
                  ? 'bg-accent-green/20 text-accent-green border border-accent-green'
                  : 'bg-bg-secondary text-text-secondary hover:text-text-primary border border-border'
              }`}
            >
              Pro OBAA
              <span className="block text-xs mt-1 opacity-70">
                Boost One Battle After Another
              </span>
            </button>
            <button
              onClick={() => setCategory('anti_sinners')}
              className={`flex-1 py-3 px-4 rounded-lg text-sm font-medium transition-colors ${
                category === 'anti_sinners'
                  ? 'bg-accent-red/20 text-accent-red border border-accent-red'
                  : 'bg-bg-secondary text-text-secondary hover:text-text-primary border border-border'
              }`}
            >
              Anti Sinners
              <span className="block text-xs mt-1 opacity-70">
                Counter the competition
              </span>
            </button>
          </div>
        </div>

        {/* Templates Selection */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium text-text-secondary">
              Templates
            </label>
            <button
              onClick={handleSelectAll}
              className="text-xs text-accent-gold hover:underline"
            >
              {selectedTemplates.length === templatesData?.templates.length
                ? 'Deselect All'
                : 'Select All'}
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {templatesData?.templates.map((template) => (
              <button
                key={template.id}
                onClick={() => handleTemplateToggle(template.id)}
                className={`px-3 py-1.5 text-xs rounded-full transition-colors ${
                  selectedTemplates.includes(template.id)
                    ? 'bg-accent-gold text-bg-primary'
                    : 'bg-bg-secondary text-text-secondary hover:text-text-primary border border-border'
                }`}
                title={template.description}
              >
                {template.name}
              </button>
            ))}
          </div>
          <p className="text-xs text-text-muted mt-2">
            {selectedTemplates.length === 0
              ? 'All templates will be used'
              : `${selectedTemplates.length} template(s) selected`}
          </p>
        </div>

        {/* Number of Memes */}
        <div>
          <label className="block text-sm font-medium text-text-secondary mb-2">
            Number of Memes: {numMemes}
          </label>
          <input
            type="range"
            min="1"
            max="12"
            value={numMemes}
            onChange={(e) => setNumMemes(parseInt(e.target.value))}
            className="w-full accent-accent-gold"
          />
          <div className="flex justify-between text-xs text-text-muted mt-1">
            <span>1</span>
            <span>12</span>
          </div>
        </div>

        {/* Tone Selection */}
        <div>
          <label className="block text-sm font-medium text-text-secondary mb-2">
            Tone
          </label>
          <div className="flex gap-3">
            {(['savage', 'sarcastic', 'playful'] as Tone[]).map((t) => (
              <button
                key={t}
                onClick={() => setTone(t)}
                className={`flex-1 py-2 px-4 rounded text-sm font-medium transition-colors capitalize ${
                  tone === t
                    ? 'bg-accent-gold text-bg-primary'
                    : 'bg-bg-secondary text-text-secondary hover:text-text-primary border border-border'
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        {/* Generate Button */}
        <button
          onClick={handleGenerate}
          disabled={generateMutation.isPending}
          className={`w-full py-3 px-6 rounded-lg text-sm font-semibold transition-all ${
            generateMutation.isPending
              ? 'bg-bg-secondary text-text-muted cursor-not-allowed'
              : 'bg-accent-gold text-bg-primary hover:bg-accent-gold/90'
          }`}
        >
          {generateMutation.isPending ? (
            <span className="flex items-center justify-center gap-2">
              <span className="inline-block w-4 h-4 border-2 border-text-muted border-t-accent-gold rounded-full animate-spin" />
              Generating...
            </span>
          ) : (
            `Generate ${numMemes} Meme${numMemes > 1 ? 's' : ''}`
          )}
        </button>

        {/* Success Message */}
        {generateMutation.isSuccess && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-4 bg-accent-green/10 border border-accent-green/30 rounded-lg"
          >
            <p className="text-accent-green text-sm font-medium">
              Successfully generated {generateMutation.data.memes.length} meme(s)
            </p>
            <p className="text-text-muted text-xs mt-1">
              Generation time: {generateMutation.data.generation_time_ms}ms
            </p>
          </motion.div>
        )}

        {/* Error Message */}
        {generateMutation.isError && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-4 bg-accent-red/10 border border-accent-red/30 rounded-lg"
          >
            <p className="text-accent-red text-sm font-medium">
              Failed to generate memes
            </p>
            <p className="text-text-muted text-xs mt-1">
              {(generateMutation.error as Error).message}
            </p>
          </motion.div>
        )}
      </div>
    </motion.section>
  );
}
