import numpy as np
from matplotlib import pyplot as plt
from spex import stokes, elements
from spectacle.general import gauss1d

# Load the input spectrum
input_spectrum = np.loadtxt("input_data/lamp_spectrum.txt", skiprows=14)
input_spectrum = input_spectrum[input_spectrum[:,0] >= 300]
# input_spectrum = input_spectrum[input_spectrum[:,0] <= 720]

# Load the SRFs
SRF_path = r"C:\Users\Burggraaff\SPECTACLE_data\iPhone_SE\calibration\iPhone_SE_spectral_response.csv"
SRF = np.loadtxt(SRF_path, delimiter=",")
SRF_wavelengths = SRF[:,0]
SRF_RGB = SRF[:,1:4]

# Create the source spectrum, fully unpolarised
wavelengths = input_spectrum[:,0]
source_intensity = input_spectrum[:,1] / np.nanmax(input_spectrum[:,1])
source = stokes.Stokes_nm(source_intensity, 0, 0, 0)

# Interpolate the SRFs to the source spectrum wavelengths
SRF_RGB_interp = np.stack([np.interp(wavelengths, SRF_wavelengths, SRF, left=0, right=0) for SRF in SRF_RGB.T])

# Create the input and output polarisers at 0 and 90 degrees, respectively
polariser_0 = elements.Linear_polarizer_general(0.9, 0.005, 0)
polariser_90 = elements.Linear_polarizer_general(0.9, 0.005, 90)

# Propagate the source light through the input polariser
after_polariser_0 = np.einsum("ij,wi->wj", polariser_0, source)

# Retardances to loop over
retardances_relative = np.linspace(0, 10, 250)
retardances_absolute = retardances_relative * 560.

# Integral of RGB intensities
integral_SRF = np.zeros((3,len(retardances_relative)))
statistic = np.zeros_like(retardances_relative)

# Create foils and propagate through them
foils = np.stack([elements.Retarder_wavelengths(retardance_absolute, 45, wavelengths) for retardance_absolute in retardances_absolute])
after_foils = np.einsum("rwij,wi->rwj", foils, after_polariser_0)

# Propagate through the output polariser
after_polariser_90 = np.einsum("ij,rwj->rwi", polariser_90, after_foils)

# Get only the total intensity spectra
intensities = after_polariser_90[...,0]

for i, (retardance_relative, retardance_absolute, intensity) in enumerate(zip(retardances_relative, retardances_absolute, intensities)):
    # Status indicator
    label = f"Retardance: {retardance_absolute:.0f} nm ; {retardance_relative:4.1f} $\lambda$"

    plt.figure(figsize=(5,4))
    plt.plot(wavelengths, intensity)
    plt.xlim(380, 720)
    plt.ylim(-0.02, 0.5)
    plt.xlabel("Wavelength [nm]")
    plt.ylabel("Intensity [a.u.]")
    plt.annotate(label, xy=(0.1,0.9), xycoords="figure fraction")
    plt.savefig(f"animation/raw_spectrum_{retardance_absolute:07.2f}.png")
    plt.close()

    # Get the intensity in RGB
    intensity_SRF = intensity * SRF_RGB_interp

    integral_SRF[:,i] = np.trapz(intensity_SRF, x=wavelengths, axis=1)

    statistic[i] = np.nanmean(gauss1d(intensity, sigma=5))

    print(retardance_absolute, "nm")

for j, c in enumerate("rgb"):
    plt.plot(retardances_relative, integral_SRF[j], c=c)
plt.xlabel("Retardance in $\lambda$ at 560 nm")
plt.ylabel("RGB value")
plt.savefig("retardance_RGB.pdf", bbox_inches="tight")
plt.show()
plt.close()

plt.plot(retardances_relative, np.rad2deg(np.arctan2(integral_SRF[0], integral_SRF[2])))
plt.xlabel("Retardance in $\lambda$ at 560 nm")
plt.ylabel("R/B hue angle [degrees]")
plt.savefig("retardance_hue.pdf", bbox_inches="tight")
plt.show()
plt.close()

plt.plot(retardances_relative, statistic)
plt.xlabel("Retardance in $\lambda$ at 560 nm")
plt.ylabel("Statistic")
plt.savefig("retardance_stat.pdf", bbox_inches="tight")
plt.show()
plt.close()
