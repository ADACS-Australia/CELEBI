process first_process{
    containerOptions '--writable'
    
    input:
         path files
    output:
         stdout
    script:
    """
        singularity run --writable /fred/oz002/askap/craft/craco/processing/containers/aips_sandbox/ bash -c "source /usr/local/aips/LOGIN.SH && cd /home/vkompell/tests && /home/vkompell/tests/testparseltongue"             
        
        #testparseltongue
        python --version
    """

}

workflow{
    input_channel=Channel.fromPath('/home/vkompell/tests/*')
    first_process(input_channel.collect())
    first_process.out.view()
}
