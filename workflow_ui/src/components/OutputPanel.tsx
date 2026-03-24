export default function OutputPanel({ verifyResult, runResult }: any) {
    return (
      <div className="output">
        {verifyResult && (
          <>
            <h4>Execution Plan</h4>
            <pre>{JSON.stringify(verifyResult.execution_plan, null, 2)}</pre>
          </>
        )}
  
        {runResult && (
          <>
            <h4>Run Result</h4>
            <pre>{JSON.stringify(runResult, null, 2)}</pre>
          </>
        )}
      </div>
    )
  }
  