function [ stdin, stdout, stderr, p ] = popen( cmd, env )
%POPEN Spawns a subprocess p via Java API and enables bidirectional
%communication with its stdin, stdout and stderr.

rt = java.lang.Runtime.getRuntime();
if numel(env) > 0
    if iscell(env)
        dim = numel(env);
        envArr = javaArray('java.lang.String',dim);
        for ii=1:dim
            envArr(ii) = java.lang.String(env{ii});
        end
    else
        envArr = javaArray('java.lang.String',1);
        envArr(1) = java.lang.String(env);
    end
    p = rt.exec(java.lang.String(cmd), envArr);
else
    p = rt.exec(java.lang.String(cmd));
end

stderr = java.io.BufferedReader(java.io.InputStreamReader(p.getErrorStream()));
stdout = java.io.BufferedReader(java.io.InputStreamReader(p.getInputStream()));
stdin = java.io.PrintWriter(p.getOutputStream());

end