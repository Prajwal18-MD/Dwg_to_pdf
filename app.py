import streamlit as st
import ezdxf
from ezdxf.addons.drawing import Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import matplotlib.pyplot as plt
import tempfile, subprocess, os

st.set_page_config(page_title="DWG/DXF → PDF")
st.title("DWG/DXF to PDF Converter")

uploaded = st.file_uploader("Upload DWG or DXF", type=["dwg", "dxf"])
if uploaded:
    suffix = os.path.splitext(uploaded.name)[1]
    # save to temp
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(uploaded.read())
        in_path = tmp.name

    # DWG→DXF via dwg2dxf if needed
    if suffix.lower() == ".dwg":
        dxf_path = in_path + ".dxf"
        try:
            subprocess.run(
                ["dwg2dxf", in_path, dxf_path],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except FileNotFoundError:
            st.error("`dwg2dxf` not found—make sure libredwg-tools is installed.")
            st.stop()
        except subprocess.CalledProcessError as e:
            st.error(f"DWG→DXF failed:\n{e.stderr.decode()}")
            st.stop()
    else:
        dxf_path = in_path

    # DXF→PDF
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
        st.download_button("Download PDF", pdf_bytes, out_name, "application/pdf")

    except Exception as e:
        st.error(f"Conversion error: {e}")

if st.button("Restart"):
    st.experimental_rerun()
