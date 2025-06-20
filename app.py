import streamlit as st
import ezdxf
from ezdxf.addons.drawing import Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import matplotlib.pyplot as plt
import tempfile, os

st.title("DXF → PDF Converter")

uploaded = st.file_uploader("Upload a DXF file", type=["dxf"])
if uploaded:
    with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as tmp:
        tmp.write(uploaded.read())
        dxf_path = tmp.name

    try:
        doc = ezdxf.readfile(dxf_path)
        msp = doc.modelspace()

        pdf_fd, pdf_path = tempfile.mkstemp(suffix=".pdf")
        os.close(pdf_fd)

        fig = plt.figure()
        backend = MatplotlibBackend(fig)
        Frontend(backend).draw_layout(msp, finalize=True)
        fig.savefig(pdf_path, format="pdf", bbox_inches="tight")
        plt.close(fig)

        pdf_bytes = open(pdf_path, "rb").read()
        out_name = os.path.splitext(uploaded.name)[0] + ".pdf"
        st.download_button("Download PDF", pdf_bytes, out_name,
                           "application/pdf")
    except Exception as e:
        st.error(f"Conversion failed: {e}")

if st.button("Restart"):
    st.experimental_rerun()
