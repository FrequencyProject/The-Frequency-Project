#!/usr/bin/env python3
"""Phase 1: Repository Configuration Validation Engine.

Executes infrastructure audits on core dependencies, required runtime modules,
and hardware microcontroller firmware configurations.
"""
import os
import sys

if sys.version_info >= (3, 11):
    import tomllib
    TOMLDecodeError = tomllib.TOMLDecodeError
else:
    try:
        import tomli as tomllib
        TOMLDecodeError = tomllib.TOMLDecodeError
    except ImportError:
        print('[ERROR] Missing required TOML parsing library. Run: pip install tomli')
        sys.exit(1)

def check_manifest_exists(path: str) -> bool:
    """Verifies existence of the target configuration file path."""
    return os.path.exists(path)

def log_validated_component(target: str):
    """Outputs verified package parameters to the terminal stream."""
    print(f' -> [VALIDATED] Structural component present: {target}')

def log_success_matrix(msg: str):
    """Outputs configuration baseline confirmation logs."""
    print(f'[SUCCESS] Infrastructure configuration matrix: {msg}')

class InfrastructureValidator:
    """Audits repository assets and file maps to ensure packaging conformity."""

    def __init__(self):
        self.manifest_file = 'pyproject.toml'
        self.firmware_file = 'firmware_adc_loop.cpp'

    def verify_repository_integrity(self) -> bool:
        """Validates core tracking modules, dependencies, and configuration constraints."""
        print('[INIT] Launching configuration and structural manifest audit...')
        
        if not check_manifest_exists(self.manifest_file):
            print(f'[CRITICAL] Operational manifest missing: {self.manifest_file}')
            return False
            
        try:
            with open(self.manifest_file, 'rb') as f:
                config_data = tomllib.load(f)
                
            project_section = config_data.get('project', {})
            dependencies = project_section.get('dependencies', [])
            setuptools_section = config_data.get('tool', {}).get('setuptools', {})
            modules = setuptools_section.get('py-modules', [])
            pytest_section = config_data.get('tool', {}).get('pytest', {}).get('ini_options', {})
            env_vars = pytest_section.get('env', [])
            
            # CRITICAL INVARIANT: Core library dependencies must be explicitly defined
            required_dependencies = ['numpy', 'scipy', 'torch', 'tpm2-pytss', 'cryptography==50.0.0']
            for req in required_dependencies:
                if not any((req in dep.replace(' ', '') for dep in dependencies)):
                    print(f'[CRITICAL] Missing required dependency specification anchor: {req}')
                    return False

            # FLEXIBLE WARNING: Check for runtime modules without crashing the build if missing
            core_runtime_modules = ['run_session', 'sensor_adapter', 'serial_daemon', 'validate_config', 'spectral_processing', 'model_architecture']
            for mod in core_runtime_modules:
                if mod not in modules:
                    print(f'[WARNING] Core runtime module mapping trace omitted from setup: {mod}')
            
            # FLEXIBLE WARNING: Verify environment variables
            required_env_vars = ['OMP_NUM_THREADS=1', 'MKL_NUM_THREADS=1', 'OPENBLAS_NUM_THREADS=1']
            for evar in required_env_vars:
                if evar not in env_vars:
                    print(f'[WARNING] Performance override constraint missing from settings: {evar}')

            # CRITICAL INVARIANT: Validate hardware settings if the bare-metal code is present
            if check_manifest_exists(self.firmware_file):
                with open(self.firmware_file, 'r') as f:
                    firmware_content = f.read()
                if 'ADC_CS_PIN = 10' not in firmware_content:
                    print('[CRITICAL] Hardware Mismatch: ADC_CS_PIN is not synchronized to native FSPI FSPICS0 (GPIO 10).')
                    return False
                if 'ADC_DRDY_PIN = 4' not in firmware_content:
                    print('[CRITICAL] Hardware Mismatch: ADC_DRDY_PIN is not synchronized to Hardware Interrupt (GPIO 4).')
                    return False
                log_validated_component('ESP32-S3 hardware pin mapping configurations.')

            log_validated_component('Project dependencies and configuration structures verified.')
            log_success_matrix('pyproject.toml loaded and validated successfully.')
            return True
            
        except TOMLDecodeError as err:
            print(f'[CRITICAL] Manifest parsing breakdown: {str(err)}')
            return False

if __name__ == '__main__':
    validator = InfrastructureValidator()
    success = validator.verify_repository_integrity()
    if not success:
        sys.exit(1)
