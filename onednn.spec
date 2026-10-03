%global _disable_lto 1

%define libname %mklibname dnnl 3
%define devname %mklibname dnnl -d

Name:		onednn
Version:	3.13.3
Release:	1
Summary:	oneDNN neural network primitives with Intel GPU SYCL
Group:		System/Libraries
License:	Apache-2.0
URL:		https://github.com/uxlfoundation/oneDNN
Source0:	%{url}/archive/refs/tags/v%{version}/oneDNN-v%{version}.tar.gz

# icpx and the Intel GPU kernels are x86_64 only.
ExclusiveArch:	x86_64 znver1

BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	intel-llvm
BuildRequires:	pkgconfig(level-zero) >= 1.32.0
BuildRequires:	pkgconfig(OpenCL)

%description
oneDNN is a library of neural-network primitives. This build uses the
DPC++ compiler, SYCL kernels for Intel GPUs and a threadpool CPU runtime
(no Intel OpenMP runtime).

ggml's SYCL backend uses it for the larger matmul and attention shapes.

%package -n %{libname}
Summary:	oneDNN shared library
Group:		System/Libraries
Provides:	onednn = %{EVRD}
Provides:	dnnl = %{EVRD}

%description -n %{libname}
Shared library for oneDNN (libdnnl).

%package -n %{devname}
Summary:	Development files for oneDNN
Group:		Development/C++
Requires:	%{libname}%{?_isa} = %{EVRD}
Requires:	intel-llvm%{?_isa}
Provides:	onednn-devel = %{EVRD}
Provides:	dnnl-devel = %{EVRD}

%description -n %{devname}
Headers and CMake package config for oneDNN. The CMake package name is DNNL.

%prep
%autosetup -n oneDNN-%{version} -p1

%build
# icpx device compilation rejects the distro -flto and -march flags.
_flags=$(printf '%s' "%{optflags}" | sed -E 's/-flto//g; s/-g3//g; s/-gdwarf-4//g; s/-mfpmath=[^ ]+//g; s/ -m[a-z0-9+.=]+//g')
_flags="$_flags -g0"
_ldflags=$(printf '%s' "%{build_ldflags}" | sed -E 's/-flto//g; s/-mfpmath=[^ ]+//g; s/ -m[a-z0-9+.=]+//g')
export CFLAGS="$_flags"
export CXXFLAGS="$_flags"
export LDFLAGS="$_ldflags"
export PATH="%{_libdir}/intel-llvm/bin:${PATH}"
export CC="%{_libdir}/intel-llvm/bin/icx"
export CXX="%{_libdir}/intel-llvm/bin/icpx"
export CMAKE_GENERATOR=Ninja
# THREADPOOL avoids icpx's Intel OpenMP runtime, which this toolchain does not ship.
%cmake \
	-DONEDNN_CPU_RUNTIME=THREADPOOL \
	-DONEDNN_GPU_RUNTIME=SYCL \
	-DONEDNN_GPU_VENDOR=INTEL \
	-DONEDNN_BUILD_EXAMPLES=OFF \
	-DONEDNN_BUILD_TESTS=OFF \
	-DONEDNN_BUILD_GRAPH=ON \
	-DONEDNN_BUILD_DOC=OFF
ninja -v

%install
DESTDIR=%{buildroot} ninja -C build install

%files -n %{libname}
%license LICENSE
%{_libdir}/libdnnl.so.3*
%{_datadir}/doc/dnnl/

%files -n %{devname}
%doc README.md
%{_includedir}/dnnl*
%dir %{_includedir}/oneapi
%{_includedir}/oneapi/dnnl/
%{_libdir}/libdnnl.so
%{_libdir}/cmake/dnnl/
