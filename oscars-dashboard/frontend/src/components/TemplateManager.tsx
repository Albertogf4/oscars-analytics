import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useTemplates, useDeleteTemplate } from '../hooks/useTemplates';
import type { TemplateInfo } from '../types/memes';

const API_BASE = 'http://localhost:8000';

interface TemplateCardProps {
  template: TemplateInfo;
  onSelect: () => void;
  isSelected: boolean;
}

function TemplateCard({ template, onSelect, isSelected }: TemplateCardProps) {
  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      whileHover={{ scale: 1.02 }}
      onClick={onSelect}
      className={`cursor-pointer rounded-xl overflow-hidden border transition-all ${
        isSelected
          ? 'border-accent-gold shadow-lg shadow-accent-gold/20'
          : 'border-border hover:border-text-secondary'
      }`}
    >
      <div className="aspect-video bg-surface relative overflow-hidden">
        <img
          src={`${API_BASE}${template.thumbnail_url}`}
          alt={template.name}
          className="w-full h-full object-contain"
          onError={(e) => {
            (e.target as HTMLImageElement).style.display = 'none';
          }}
        />
        <div className="absolute top-2 right-2">
          <span className="px-2 py-1 bg-black/70 rounded-full text-xs text-white">
            {template.text_slots} slot{template.text_slots !== 1 ? 's' : ''}
          </span>
        </div>
      </div>
      <div className="p-3 bg-surface-secondary">
        <h4 className="font-semibold text-text-primary text-sm truncate">
          {template.name}
        </h4>
        <p className="text-xs text-text-secondary mt-1 truncate">
          {template.irony_type.replace(/_/g, ' ')}
        </p>
      </div>
    </motion.div>
  );
}

interface TemplateDetailProps {
  template: TemplateInfo;
  onClose: () => void;
}

function TemplateDetail({ template, onClose }: TemplateDetailProps) {
  const deleteMutation = useDeleteTemplate();

  const handleDelete = async () => {
    if (!confirm(`Are you sure you want to delete "${template.name}"?`)) {
      return;
    }

    await deleteMutation.mutateAsync(template.id);
    onClose();
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className="bg-surface-secondary rounded-xl p-6 sticky top-4"
    >
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-xl font-semibold text-text-primary">{template.name}</h3>
        <button
          onClick={onClose}
          className="text-text-secondary hover:text-text-primary"
        >
          ✕
        </button>
      </div>

      <img
        src={`${API_BASE}${template.thumbnail_url}`}
        alt={template.name}
        className="w-full rounded-lg mb-4"
      />

      <div className="space-y-4 text-sm">
        <div>
          <h4 className="text-text-secondary mb-1">ID</h4>
          <code className="text-text-primary bg-surface px-2 py-1 rounded">
            {template.id}
          </code>
        </div>

        <div>
          <h4 className="text-text-secondary mb-1">Description</h4>
          <p className="text-text-primary">{template.description}</p>
        </div>

        <div>
          <h4 className="text-text-secondary mb-1">Irony Type</h4>
          <span className="inline-block px-3 py-1 bg-accent-gold/20 text-accent-gold rounded-full">
            {template.irony_type.replace(/_/g, ' ')}
          </span>
        </div>

        <div>
          <h4 className="text-text-secondary mb-2">Text Slots ({template.text_slots})</h4>
          <div className="flex flex-wrap gap-2">
            {template.slot_names.map((slot) => (
              <span
                key={slot}
                className="px-2 py-1 bg-surface rounded text-text-primary"
              >
                {slot}
              </span>
            ))}
          </div>
        </div>

        <div>
          <h4 className="text-text-secondary mb-1">Character Limit</h4>
          <p className="text-text-primary">
            {template.max_chars_per_slot} characters per slot
          </p>
        </div>
      </div>

      <div className="mt-6 pt-4 border-t border-border">
        <button
          onClick={handleDelete}
          disabled={deleteMutation.isPending}
          className="w-full px-4 py-2 bg-red-500/10 text-red-400 border border-red-500/30 rounded-lg hover:bg-red-500/20 transition-colors disabled:opacity-50"
        >
          {deleteMutation.isPending ? 'Deleting...' : 'Delete Template'}
        </button>
        {deleteMutation.isSuccess && (
          <p className="text-sm text-text-secondary mt-2">
            Template marked for deletion. Manual file edits required.
          </p>
        )}
      </div>
    </motion.div>
  );
}

export function TemplateManager() {
  const { data, isLoading, error } = useTemplates();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>('');
  const [slotFilter, setSlotFilter] = useState<number | null>(null);

  const selectedTemplate = data?.templates.find((t) => t.id === selectedId);

  // Filter templates
  const filteredTemplates = data?.templates.filter((template) => {
    const matchesSearch =
      !filter ||
      template.name.toLowerCase().includes(filter.toLowerCase()) ||
      template.irony_type.toLowerCase().includes(filter.toLowerCase());

    const matchesSlots = slotFilter === null || template.text_slots === slotFilter;

    return matchesSearch && matchesSlots;
  });

  // Get unique slot counts for filter
  const slotCounts = [...new Set(data?.templates.map((t) => t.text_slots) || [])].sort();

  if (isLoading) {
    return (
      <div className="bg-surface-secondary rounded-xl p-8 text-center">
        <div className="animate-spin w-8 h-8 border-2 border-accent-gold border-t-transparent rounded-full mx-auto mb-4" />
        <p className="text-text-secondary">Loading templates...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-8 text-center">
        <p className="text-red-400">Failed to load templates: {error.message}</p>
      </div>
    );
  }

  return (
    <div className="flex gap-6">
      {/* Template Grid */}
      <div className="flex-1">
        <div className="flex items-center gap-4 mb-6">
          <h3 className="text-xl font-semibold text-text-primary">
            Templates ({data?.total || 0})
          </h3>

          {/* Search */}
          <input
            type="text"
            placeholder="Search templates..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="flex-1 max-w-xs bg-surface border border-border rounded-lg px-3 py-2 text-text-primary placeholder:text-text-secondary"
          />

          {/* Slot Filter */}
          <div className="flex gap-2">
            <button
              onClick={() => setSlotFilter(null)}
              className={`px-3 py-1 rounded-full text-sm ${
                slotFilter === null
                  ? 'bg-accent-gold text-black'
                  : 'bg-surface text-text-secondary hover:text-text-primary'
              }`}
            >
              All
            </button>
            {slotCounts.map((count) => (
              <button
                key={count}
                onClick={() => setSlotFilter(count)}
                className={`px-3 py-1 rounded-full text-sm ${
                  slotFilter === count
                    ? 'bg-accent-gold text-black'
                    : 'bg-surface text-text-secondary hover:text-text-primary'
                }`}
              >
                {count} slot{count !== 1 ? 's' : ''}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <AnimatePresence mode="popLayout">
            {filteredTemplates?.map((template) => (
              <TemplateCard
                key={template.id}
                template={template}
                onSelect={() => setSelectedId(template.id === selectedId ? null : template.id)}
                isSelected={template.id === selectedId}
              />
            ))}
          </AnimatePresence>
        </div>

        {filteredTemplates?.length === 0 && (
          <div className="text-center py-12 text-text-secondary">
            No templates match your filters
          </div>
        )}
      </div>

      {/* Detail Panel */}
      <AnimatePresence>
        {selectedTemplate && (
          <div className="w-80 flex-shrink-0">
            <TemplateDetail
              template={selectedTemplate}
              onClose={() => setSelectedId(null)}
            />
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
