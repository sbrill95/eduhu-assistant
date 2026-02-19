import type { Artifact } from '@/lib/types';
import { DocxPreview } from './DocxPreview';
import { H5PPlayer } from '@/components/exercises/H5PPlayer';

interface Props {
  artifact: Artifact;
}

export function ArtifactContent({ artifact }: Props) {
  switch (artifact.type) {
    case 'docx':
      return <DocxPreview url={artifact.url} />;
    case 'h5p':
      return <H5PPlayer exerciseId={artifact.id} />;
    case 'audio':
      return (
        <div className="flex items-center justify-center h-full">
          <audio controls src={artifact.url} className="w-full max-w-md" />
        </div>
      );
    case 'image':
      return (
        <div className="flex items-center justify-center">
          <img src={artifact.url} alt={artifact.title} className="max-w-full rounded-lg shadow-md" />
        </div>
      );
    default:
      return null;
  }
}
