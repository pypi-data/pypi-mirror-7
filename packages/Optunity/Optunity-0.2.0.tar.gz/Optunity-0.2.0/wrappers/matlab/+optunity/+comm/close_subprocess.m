function close_subprocess( m2py, py2m, stderr, subprocess )
%CLOSE_SUBPROCESS Closes all communication and destroys subprocess.

m2py.close();
py2m.close();
stderr.close();
subprocess.destroy();

end

