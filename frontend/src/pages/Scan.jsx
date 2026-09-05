import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { UploadCloud, ScanLine, CheckCircle2 } from 'lucide-react'

export default function Scan() {

  const navigate = useNavigate()
  const [selectedFile, setSelectedFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [detected, setDetected] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // When user selects an image
  const handleFileChange = (event) => {

    const file = event.target.files[0]

    if (!file) return

    // Check file type
    if (!file.type.startsWith('image/')) {
      setError('Please upload an image file.')
      return
    }

    // Check file size (5 MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('Image must be smaller than 5 MB.')
      return
    }

    setSelectedFile(file)

    // Create preview
    setPreview(URL.createObjectURL(file))

    // Clear old results
    setDetected([])
    setError('')
  }


  // Send image to FastAPI
  const scanProduct = async () => {

    if (!selectedFile) {
      setError('Please choose a product image first.')
      return
    }

    setLoading(true)
    setError('')
    setDetected([])

    const formData = new FormData()

    // IMPORTANT:
    // "file" must match FastAPI's UploadFile parameter
    formData.append('file', selectedFile)

    try {

      const response = await fetch('/api/scan', {
        method: 'POST',
      body: formData,
      } 
    )

      if (!response.ok) {
        throw new Error('OCR request failed')
      }

      const data = await response.json()

      console.log('OCR response:', data)

      /*
        Backend response expected:

        {
          "filename": "bottle.jpg",
          "extracted_text": [
            "ABC",
            "STAINLESS STEEL",
            "1 LITRE",
            "BPA FREE"
          ]
        }
      */

      setDetected(data.extracted_text || [])

    } catch (err) {

      console.error(err)

      setError(
        'Unable to connect to BIS SĀRTHI backend. Make sure FastAPI is running on port 8000.'
      )

    } finally {

      setLoading(false)

    }
  }


  return (

    <div className="mx-auto max-w-4xl px-6 py-14">

      {/* HEADER */}

      <div className="text-center">

        <span className="inline-flex items-center gap-2 rounded-full bg-saffron-100 px-3 py-1 text-xs font-bold uppercase tracking-wide text-saffron-600">

          <ScanLine className="h-3.5 w-3.5" />

          Product Scanner

        </span>


        <h1 className="font-display mt-4 text-3xl font-bold text-navy-900">

          Upload a photo — we'll read the rest

        </h1>


        <p className="mx-auto mt-2 max-w-xl text-navy-700/65">

          Product photos, labels, or spec sheets. We'll always show what we detected before using it.

        </p>

      </div>


      {/* MAIN GRID */}

      <div className="mt-10 grid grid-cols-1 gap-6 lg:grid-cols-2">


        {/* LEFT SIDE — UPLOAD */}

        <div className="card flex flex-col items-center justify-center gap-3 border-2 border-dashed border-navy-900/15 p-12 text-center">

          <UploadCloud className="h-10 w-10 text-navy-700/40" />


          <p className="text-sm font-semibold text-navy-800">

            Drag & drop an image, or click to upload

          </p>


          <p className="text-xs text-navy-700/50">

            JPG, PNG or WEBP · up to 5MB

          </p>


          {/* HIDDEN FILE INPUT */}

          <input
            id="product-image"
            type="file"
            accept="image/png,image/jpeg,image/webp"
            onChange={handleFileChange}
            className="hidden"
          />


          {/* CHOOSE FILE BUTTON */}

          <label
            htmlFor="product-image"
            className="mt-2 cursor-pointer rounded-full bg-navy-900 px-5 py-2 text-sm font-semibold text-white hover:bg-navy-800"
          >

            Choose File

          </label>


          {/* FILE NAME */}

          {selectedFile && (

            <p className="mt-3 text-xs font-medium text-navy-700">

              Selected: {selectedFile.name}

            </p>

          )}


          {/* IMAGE PREVIEW */}

          {preview && (

            <img
              src={preview}
              alt="Selected product"
              className="mt-4 max-h-48 rounded-lg object-contain"
            />

          )}


          {/* SCAN BUTTON */}

          <button
            onClick={scanProduct}
            disabled={!selectedFile || loading}
            className="mt-4 rounded-full bg-saffron-500 px-6 py-2.5 text-sm font-semibold text-white hover:bg-saffron-600 disabled:cursor-not-allowed disabled:opacity-50"
          >

            {loading ? 'Scanning...' : '🔍 Scan Product'}

          </button>


          {/* ERROR */}

          {error && (

            <p className="mt-3 text-xs font-medium text-red-600">

              {error}

            </p>

          )}

        </div>


        {/* RIGHT SIDE — RESULTS */}

        <div className="card p-6">

          <div className="flex items-center justify-between">

            <h2 className="font-display text-sm font-bold text-navy-900">

              We detected the following

            </h2>


            <span className="rounded-full bg-verified-100 px-2.5 py-1 text-[11px] font-bold text-verified-600">

              Please verify

            </span>

          </div>


          {/* BEFORE SCAN */}

          {detected.length === 0 && !loading && (

            <p className="mt-6 text-sm text-navy-700/50">

              Upload and scan a product image to see detected information.

            </p>

          )}


          {/* LOADING */}

          {loading && (

            <p className="mt-6 text-sm text-navy-700/60">

              🔍 Reading product image...

            </p>

          )}


          {/* RESULTS */}

          {detected.length > 0 && (

            <dl className="mt-4 divide-y divide-navy-900/5">

              {detected.map((text, index) => (

                <div
                  key={index}
                  className="flex items-center justify-between py-3"
                >

                  <dt className="text-xs text-navy-700/50">

                    Detected Text {index + 1}

                  </dt>

                  <dd className="text-sm font-semibold text-navy-900">

                    {text}

                  </dd>

                </div>

              ))}

            </dl>

          )}


          {/* CONFIRM */}

{detected.length > 0 && (

  <button
    onClick={() =>
      navigate('/standards', {
        state: { detectedText: detected }
      })
    }
    className="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-full bg-saffron-500 px-5 py-2.5 text-sm font-semibold text-white hover:bg-saffron-600"
  >

    <CheckCircle2 className="h-4 w-4" />

    Confirm & Find Standards

  </button>

)}

        </div>

      </div>

    </div>

  )
}