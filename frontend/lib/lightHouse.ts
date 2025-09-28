"use client"

/** Lighthouse simple client (upload + list) */

type UploadProgress = (pct: number) => void

const API_BASE = "https://node.lighthouse.storage"
const ADD_ENDPOINT = `${API_BASE}/api/v0/add`
const LIST_ENDPOINT = `https://api.lighthouse.storage/api/v0/me/files`

function getApiKey() {
  const key = process.env.NEXT_PUBLIC_LIGHTHOUSE_API_KEY
  if (!key) {
    throw new Error("Missing NEXT_PUBLIC_LIGHTHOUSE_API_KEY")
  }
  return key
}

function safeParseJson(text: string) {
  try {
    return JSON.parse(text)
  } catch {
    const snippet = text.slice(0, 300)
    throw new Error(`Lighthouse response was not JSON. First 300 chars:\n${snippet}`)
  }
}

/** XHR to report progress */
function xhrUpload(form: FormData, { onProgress }: { onProgress?: UploadProgress } = {}) {
  return new Promise<any>((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open("POST", ADD_ENDPOINT, true)
    xhr.responseType = "text"
    xhr.setRequestHeader("Authorization", `Bearer ${getApiKey()}`)

    xhr.upload.onprogress = (e) => {
      if (!onProgress || !e.lengthComputable) return
      const pct = Math.round((e.loaded / e.total) * 100)
      onProgress(pct)
    }

    xhr.onerror = () => reject(new Error("Network error during Lighthouse upload"))
    xhr.ontimeout = () => reject(new Error("Lighthouse upload timed out"))
    xhr.onload = () => {
      const text = xhr.responseText ?? ""
      if (xhr.status < 200 || xhr.status >= 300) {
        const piece = text.slice(0, 300)
        reject(new Error(`Lighthouse upload failed (HTTP ${xhr.status}).\n${piece}`))
        return
      }
      const data = safeParseJson(text)
      resolve(data)
    }

    xhr.send(form)
  })
}

/** Public gateway URL for a CID. */
export function lighthouseCidUrl(cid?: string | null) {
  if (!cid) return "#"
  return `https://gateway.lighthouse.storage/ipfs/${cid}`
}

/** Uploads a single file (Blob/File) to Lighthouse. */
export async function uploadFileToLighthouse(
  file: File | Blob,
  onProgress?: UploadProgress
): Promise<{ cid: string; name: string; size: number }> {
  const form = new FormData()
  const filename = (file as File).name || "upload.bin"
  form.append("file", file, filename)

  const res = await xhrUpload(form, { onProgress })
  const data = res?.data || res
  const hash = data?.Hash || data?.hash || data?.cid
  const name = data?.Name || filename
  const sizeStr = data?.Size || data?.size

  if (!hash) throw new Error(`Unexpected Lighthouse response: ${JSON.stringify(res).slice(0, 200)}`)

  return { cid: String(hash), name: String(name), size: Number(sizeStr ?? 0) }
}

/** Uploads a JSON document to Lighthouse. */
export async function uploadJsonToLighthouse(
  obj: any,
  filename = "metadata.json",
  onProgress?: UploadProgress
) {
  const blob = new Blob([JSON.stringify(obj)], { type: "application/json" })
  const file = new File([blob], filename, { type: "application/json" })
  return uploadFileToLighthouse(file, onProgress)
}

/** Paginated list of your uploads (auth = API key). */
export async function listUploads(params?: { limit?: number; page?: number }) {
  const limit = params?.limit ?? 50
  const page = params?.page ?? 1
  const res = await fetch(`${LIST_ENDPOINT}?limit=${limit}&page=${page}`, {
    headers: { Authorization: `Bearer ${getApiKey()}` },
    cache: "no-store",
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Lighthouse list failed (${res.status}). ${text.slice(0, 200)}`)
  }
  const data = await res.json()
  // Normalize to { data: { fileList: [...] } }
  const fileList = data?.data?.fileList ?? data?.fileList ?? []
  return { data: { fileList } }
}
