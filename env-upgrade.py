import subprocess
import sys
import pkg_resources


def upgrade_all():
    """
    Upgrade all outdated packages in the current environment.

    This function retrieves a list of outdated packages in the current environment
    and upgrades them using the `pip` package manager.

    :return: None
    """
    outdated_packages = {
        dist.project_name: dist.version for dist in pkg_resources.working_set}
    for package in outdated_packages:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--upgrade", package])


# Call the function
upgrade_all()
