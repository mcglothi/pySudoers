# pySudoers

<p>This Python script processes the /etc/sudoers file and creates individual files in /etc/sudoers.d directory for each user or group that has sudo privileges, following the sudoers file format.</p>

<h2>Usage</h2>

<p>The script can be run from the command line as follows:</p>

<pre><code>
python3 pySudoers.py [options]
</code></pre>

<h2>Options</h2>

<p>The script accepts the following command line options:</p>
<ul>
<li><code>-s</code> or <code>--sudoers-file</code>: Specifies the path to the sudoers file. Default is <code>/etc/sudoers</code>.</li>

<li><code>-p</code> or <code>--file-prefix</code>: Specifies the prefix for the sudoers.d files. Default is <code>10</code>.</li>

<li><code>-d</code> or <code>--sudoers-d-dir</code>: Specifies the directory for the sudoers.d files. Default is <code>/etc/sudoers.d</code>.</li>

<li><code>-t</code> or <code>--test</code>: Runs the script in test mode. In this mode, the script will not make any changes, but will print out what it would do.</li>

<li><code>-r</code> or <code>--remove</code>: If specified, the script will remove entries from the sudoers file after moving them to individual files in the sudoers.d directory.</li>

<li><code>-b</code> or <code>--backup</code>: If specified, the script will create backups of the sudoers file and the sudoers.d directory before making any changes.</li>
</ul>

<h2>Features</h2>

<ul>
<li>The script reads the sudoers file line by line and checks for user or group rules.</li>

<li>For each rule, the script checks whether a corresponding file already exists in the sudoers.d directory. If not, it creates a new file with the rule.</li>

<li>The script uses <code>visudo -cf</code> to check the syntax of each newly created file. If <code>visudo</code> reports an error, the script deletes the file.</li>

<li>If the <code>--remove</code> option is specified, the script removes the corresponding entry from the sudoers file after creating each new file.</li>

<li>If the <code>--backup</code> option is specified, the script creates backups of the sudoers file and the sudoers.d directory before making any changes.</li>
</ul>

<h2>Requirements</h2>

<ul>
<li>Python 3.6 or later.</li>

<li>The script must be run with sudo or root privileges in order to read the sudoers file and write to the sudoers.d directory.</li>
</ul>

<h2>Disclaimer</h2>

<p>This script makes changes to your system's sudo configuration. Incorrect sudo configuration can lock you out of your system or give unauthorized users sudo privileges. Always review the changes made by the script and use the <code>--test</code> mode to see what changes would be made before running the script. Always keep backups of your sudoers file and sudoers.d directory. The author of this script is not responsible for any damage caused by the use or misuse of this script.</p>
