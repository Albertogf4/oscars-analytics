import { useState, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useUploadTemplate, useProcessingStatus, useFinalizeTemplate } from '../hooks/useTemplates';
import type { TemplateProcessingResult } from '../types/memes';

const FUN_MESSAGES = [
  "Teaching AI about irony...",
  "Analyzing meme potential...",
  "Counting pixels with purpose...",
  "Decoding internet humor...",
  "Consulting the meme council...",
  "Extracting dankness levels...",
  "Calibrating humor sensors...",
  "Reading between the panels...",
  "Channeling meme energy...",
  "Processing maximum kino...",
  "Unlocking template secrets...",
  "Summoning the meme gods...",
  "Calculating irony coefficients...",
  "Mining for comedy gold...",
  "Optimizing for virality...",
];

const STAGE_NAMES: Record<string, string> = {
  visual: 'Visual Analysis',
  slots: 'Slot Detection',
  irony: 'Irony Analysis',
  metadata: 'Metadata Generation',
  examples: 'Example Generation',
  prompt: 'Prompt Writing',
  code: 'Code Generation',
};

const STAGE_ORDER = ['visual', 'slots', 'irony', 'metadata', 'examples', 'prompt', 'code'];

export function TemplateUploader() {
  const [dragActive, setDragActive] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [editedMetadata, setEditedMetadata] = useState<{
    id?: string;
    name?: string;
    description?: string;
  }>({});
  const [messageIndex, setMessageIndex] = useState(0);

  const uploadMutation = useUploadTemplate();
  const { data: status, isLoading: statusLoading, isFetching, isPending } = useProcessingStatus(jobId);
  const finalizeMutation = useFinalizeTemplate();

  // Debug: log state changes
  console.log('TemplateUploader state:', {
    jobId,
    statusLoading,
    isFetching,
    isPending,
    status: status?.status,
    uploadPending: uploadMutation.isPending
  });

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  }, []);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  }, []);

  const handleFile = async (file: File) => {
    // Create preview URL
    setPreviewUrl(URL.createObjectURL(file));

    // Upload and start processing
    const response = await uploadMutation.mutateAsync(file);
    setJobId(response.job_id);
  };

  const handleFinalize = async () => {
    if (!jobId) return;

    await finalizeMutation.mutateAsync({
      job_id: jobId,
      metadata_overrides: Object.keys(editedMetadata).length > 0 ? editedMetadata : undefined,
    });
  };

  const reset = () => {
    setJobId(null);
    setPreviewUrl(null);
    setEditedMetadata({});
    uploadMutation.reset();
    finalizeMutation.reset();
  };

  const isProcessing = status?.status === 'pending' || status?.status === 'running';
  const isCompleted = status?.status === 'completed';
  const isFailed = status?.status === 'failed';
  const result = status?.result as TemplateProcessingResult | undefined;
  const currentMessage = FUN_MESSAGES[messageIndex];

  // Rotate fun messages during processing
  // Use multiple loading indicators for React Query v5 compatibility
  const showLoader = statusLoading || isFetching || isPending || isProcessing;

  useEffect(() => {
    if (!showLoader) return;

    const interval = setInterval(() => {
      setMessageIndex((prev) => (prev + 1) % FUN_MESSAGES.length);
    }, 2500);

    return () => clearInterval(interval);
  }, [showLoader]);

  return (
    <div className="bg-surface-secondary rounded-xl p-6 mb-8">
      <h3 className="text-xl font-semibold text-text-primary mb-4">
        Add New Template
      </h3>

      {!jobId ? (
        // Upload Zone
        <div
          className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer ${
            dragActive
              ? 'border-accent-gold bg-accent-gold/10'
              : 'border-border hover:border-accent-gold/50'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => document.getElementById('file-input')?.click()}
        >
          <input
            id="file-input"
            type="file"
            accept="image/*"
            className="hidden"
            onChange={handleFileInput}
          />
          <div className="text-4xl mb-4">🖼️</div>
          <p className="text-text-primary font-medium mb-2">
            Drop a meme template image here
          </p>
          <p className="text-text-secondary text-sm">
            or click to browse (PNG, JPG, WebP)
          </p>
        </div>
      ) : (
        // Processing View
        <div className="space-y-6">
          {/* Upload Success Banner */}
          {uploadMutation.isSuccess && !isCompleted && !isFailed && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-green-500/10 border border-green-500/30 rounded-lg p-3"
            >
              <p className="text-green-400 text-sm flex items-center gap-2">
                <span>✓</span> Template uploaded successfully! Processing started...
              </p>
            </motion.div>
          )}

          <div className="flex gap-6">
            {/* Image Preview */}
            {previewUrl && (
              <div className="w-48 flex-shrink-0">
                <img
                  src={previewUrl}
                  alt="Template preview"
                  className="w-full rounded-lg border border-border"
                />
              </div>
            )}

            {/* Processing Status */}
            <div className="flex-1 space-y-4">
              {/* Progress Bar */}
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-text-secondary">
                    {isProcessing ? `Processing: ${STAGE_NAMES[status?.current_stage || 'visual']}` :
                     isCompleted ? 'Processing Complete' :
                     isFailed ? 'Processing Failed' : 'Starting...'}
                  </span>
                  <span className="text-text-primary font-medium">
                    {status?.progress_percent || 0}%
                  </span>
                </div>
                <div className="h-2 bg-surface rounded-full overflow-hidden">
                  <motion.div
                    className={`h-full ${isFailed ? 'bg-red-500' : 'bg-accent-gold'}`}
                    initial={{ width: 0 }}
                    animate={{ width: `${status?.progress_percent || 0}%` }}
                    transition={{ duration: 0.3 }}
                  />
                </div>
              </div>

              {/* Stage Indicators */}
              <div className="flex gap-2 flex-wrap">
                {STAGE_ORDER.map((stage) => {
                  const completed = status?.stages_completed?.includes(stage);
                  const current = status?.current_stage === stage && isProcessing;

                  return (
                    <motion.span
                      key={stage}
                      initial={false}
                      animate={completed ? { scale: [1, 1.15, 1] } : {}}
                      transition={{ duration: 0.3 }}
                      className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                        completed
                          ? 'bg-green-500/20 text-green-400'
                          : current
                          ? 'bg-accent-gold/20 text-accent-gold'
                          : 'bg-surface text-text-secondary'
                      }`}
                    >
                      {completed && (
                        <motion.span
                          initial={{ scale: 0, opacity: 0 }}
                          animate={{ scale: 1, opacity: 1 }}
                          transition={{ type: "spring", stiffness: 500, damping: 15 }}
                          className="inline-block mr-1"
                        >
                          ✓
                        </motion.span>
                      )}
                      {current && (
                        <motion.span
                          animate={{ opacity: [1, 0.5, 1] }}
                          transition={{ duration: 1.5, repeat: Infinity }}
                          className="inline-block mr-1"
                        >
                          ⟳
                        </motion.span>
                      )}
                      {STAGE_NAMES[stage]}
                    </motion.span>
                  );
                })}
              </div>

              {/* Spinning Loader with Fun Message */}
              {showLoader && (
                <div className="flex flex-col items-center gap-3 py-4">
                  <motion.div
                    className="w-10 h-10 border-4 border-accent-gold/30 border-t-accent-gold rounded-full"
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  />
                  <AnimatePresence mode="wait">
                    <motion.p
                      key={currentMessage}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      transition={{ duration: 0.3 }}
                      className="text-text-secondary text-sm italic"
                    >
                      {currentMessage}
                    </motion.p>
                  </AnimatePresence>
                </div>
              )}

              {/* Error Message */}
              {isFailed && status?.error && (
                <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                  <p className="text-red-400 text-sm">{status.error}</p>
                </div>
              )}
            </div>
          </div>

          {/* Results Preview */}
          <AnimatePresence>
            {isCompleted && result && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="border border-border rounded-lg p-4 space-y-4"
              >
                <h4 className="text-lg font-semibold text-text-primary">
                  Extracted Information
                </h4>

                {/* Editable Metadata */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-text-secondary mb-1">
                      Template ID
                    </label>
                    <input
                      type="text"
                      value={editedMetadata.id ?? result.metadata.id}
                      onChange={(e) => setEditedMetadata({ ...editedMetadata, id: e.target.value })}
                      className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-text-primary"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-text-secondary mb-1">
                      Template Name
                    </label>
                    <input
                      type="text"
                      value={editedMetadata.name ?? result.metadata.name}
                      onChange={(e) => setEditedMetadata({ ...editedMetadata, name: e.target.value })}
                      className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-text-primary"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm text-text-secondary mb-1">
                    Description
                  </label>
                  <textarea
                    value={editedMetadata.description ?? result.metadata.description}
                    onChange={(e) => setEditedMetadata({ ...editedMetadata, description: e.target.value })}
                    rows={2}
                    className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-text-primary resize-none"
                  />
                </div>

                {/* Irony Analysis Preview */}
                <div className="bg-surface rounded-lg p-4">
                  <h5 className="text-sm font-semibold text-accent-gold mb-2">
                    Irony Analysis
                  </h5>
                  <div className="space-y-2 text-sm">
                    <p>
                      <span className="text-text-secondary">Type:</span>{' '}
                      <span className="text-text-primary">{result.irony_analysis.irony_type}</span>
                    </p>
                    <p>
                      <span className="text-text-secondary">Tone:</span>{' '}
                      <span className="text-text-primary">{result.irony_analysis.tone}</span>
                    </p>
                    <p className="text-text-secondary">
                      {result.irony_analysis.irony_explanation}
                    </p>
                  </div>
                </div>

                {/* Slot Detection Preview */}
                <div className="bg-surface rounded-lg p-4">
                  <h5 className="text-sm font-semibold text-accent-gold mb-2">
                    Text Slots ({result.slot_detection.text_slots})
                  </h5>
                  <div className="flex gap-2 flex-wrap">
                    {result.slot_detection.slot_names.map((slot, i) => (
                      <span
                        key={slot}
                        className="px-3 py-1 bg-surface-secondary rounded-full text-sm text-text-primary"
                      >
                        {slot}: {result.slot_detection.slot_descriptions[i]}
                      </span>
                    ))}
                  </div>
                  <p className="text-xs text-text-secondary mt-2">
                    Max {result.slot_detection.max_chars_per_slot} characters per slot
                  </p>
                </div>

                {/* Example Preview */}
                <div className="bg-surface rounded-lg p-4">
                  <h5 className="text-sm font-semibold text-accent-gold mb-2">
                    Example Content
                  </h5>
                  <div className="text-sm text-text-primary">
                    {result.examples.example.map((slot) => (
                      <p key={slot.slot_name}>
                        <span className="text-text-secondary">{slot.slot_name}:</span> "{slot.text}"
                      </p>
                    ))}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-3 pt-4">
                  <button
                    onClick={handleFinalize}
                    disabled={finalizeMutation.isPending}
                    className="flex-1 px-4 py-2 bg-accent-gold text-black font-semibold rounded-lg hover:bg-accent-gold/90 transition-colors disabled:opacity-50"
                  >
                    {finalizeMutation.isPending ? 'Integrating...' : 'Integrate Template'}
                  </button>
                  <button
                    onClick={reset}
                    className="px-4 py-2 bg-surface border border-border text-text-primary rounded-lg hover:border-text-secondary transition-colors"
                  >
                    Cancel
                  </button>
                </div>

                {/* Finalize Result */}
                {finalizeMutation.isSuccess && (
                  <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4">
                    <p className="text-green-400 font-medium">
                      {finalizeMutation.data.message}
                    </p>
                    <button
                      onClick={reset}
                      className="mt-2 text-sm text-accent-gold hover:underline"
                    >
                      Add another template
                    </button>
                  </div>
                )}

                {finalizeMutation.isError && (
                  <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                    <p className="text-red-400 text-sm">
                      {finalizeMutation.error.message}
                    </p>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}

      {uploadMutation.isError && (
        <div className="mt-4 bg-red-500/10 border border-red-500/30 rounded-lg p-4">
          <p className="text-red-400 text-sm">{uploadMutation.error.message}</p>
        </div>
      )}
    </div>
  );
}
