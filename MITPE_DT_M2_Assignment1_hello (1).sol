pragma solidity ^0.5.0;
contract Hello {
    string constant a = "Hello World";
    function get() public pure returns (string memory){
        return a;
    }
}