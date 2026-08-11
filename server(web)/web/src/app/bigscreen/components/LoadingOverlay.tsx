export function LoadingOverlay({ progress, hidden }: { progress: number; hidden: boolean }) {
  return (
    <div className={`lra-loading ${hidden ? 'lra-loading-hidden' : ''}`}>
      <div className="lra-loading-text">
        {'LOADING'.split('').map((char, index) => (
          <span key={index} style={{ ['--index' as string]: index + 1 }}>
            {char}
          </span>
        ))}
      </div>
      <div className="lra-loading-progress">
        <span className="value">{Math.floor(progress)}</span>
        <span className="unit">%</span>
      </div>
    </div>
  );
}
