
import { MultiChoicePlayer } from './MultiChoicePlayer';
import { BlanksPlayer } from './BlanksPlayer';
import { TrueFalsePlayer } from './TrueFalsePlayer';

export function ExercisePlayer({ h5pType, content }: { h5pType: string; content: any }) {
  switch (h5pType) {
    case 'H5P.MultiChoice':
      return <MultiChoicePlayer content={content} />;
    case 'H5P.Blanks':
      return <BlanksPlayer content={content} />;
    case 'H5P.TrueFalse':
      return <TrueFalsePlayer content={content} />;
    default:
      return <pre>{JSON.stringify(content, null, 2)}</pre>;
  }
}