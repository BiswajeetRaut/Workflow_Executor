import axios from "axios"

const BASE_URL = "http://localhost:8000"

export async function verifyWorkflow(payload: any) {
  const res = await axios.post(`${BASE_URL}/verify`, payload)
  return res.data
}

export async function runWorkflow(executionPlan: any) {
  const res = await axios.post(`${BASE_URL}/run`, {
    execution_plan: executionPlan,
    inputs: {}
  })
  return res.data
}
